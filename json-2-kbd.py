import argparse
import json
import os
from binary_reader import BinaryReader


def get_button_type(button):
    if button == 'Circle':
        return 0
    elif button == 'Cross':
        return 1
    elif button == 'Square':
        return 2
    elif button == 'Triangle':
        return 3
    else:
        print(f'Invalid button {button}!')
        raise ValueError


def get_note_type(note):
    if note == 'Regular':
        return 0
    elif note == 'Hold':
        return 1
    elif note == 'Rapid':
        return 2
    else:
        print(f'Invalid note {note}!')
        raise ValueError

def convert_to_pos(ms):
    if ms != 0:
        return int(ms * 3)
    else:
        return 0


def write_pos(kbd, content, ms_mode):
    if ms_mode:
        kbd.write_uint32(convert_to_pos(content))
    else:
        kbd.write_uint32(content)

def import_to_kbd(input_file, output_file, cutscene_start):
    with open(input_file) as f:
        data = json.loads(f.read())
    kbd = BinaryReader(bytearray())

    # HEADER
    kbd.write_str('NTBK')  # magic
    kbd.write_uint32(0)
    kbd.write_uint32(data['Header']['Version'])
    size_pos = kbd.pos()
    kbd.write_uint32(0)  # size
    kbd.write_uint32(len(data['Notes']))
    score_pos = kbd.pos()
    kbd.write_uint32(0)  # max score
    if data['Header']['Version'] > 1:
            kbd.write_uint32(data['Header']['Max score pre-cutscene'])
    ms_mode = data['Header']['Converted to milliseconds']

    # NOTES
    i = 0
    max_score = 0
    max_cutscene_score = 0
    cutscene_start = cutscene_start * 1000
    while i < len(data['Notes']):
        note = data['Notes'][i]
        write_pos(kbd, note['Start position'], ms_mode)
        write_pos(kbd, note['End position'], ms_mode)
        kbd.write_uint32(note['Vertical position'])
        kbd.write_uint32(0)
        kbd.write_uint32(get_button_type(note['Button type']))
        kbd.write_uint32(get_note_type(note['Note type']))
        if get_note_type(note['Note type']) == 0:
            max_score += 10
        else:
            max_score += 30

        if i > 19:
            max_score += 5
        kbd.write_uint16(note['Cue ID'])
        kbd.write_uint16(note['Cuesheet ID'])
        kbd.write_uint32(0)

        if cutscene_start:
            if cutscene_start > note['Start position']:
                max_cutscene_score = max_score
        i += 1

    kbd.seek(size_pos)

    if data['Header']['Version'] > 1:
        header_size = 0x1C
    else:
        header_size = 0x18

    kbd.write_uint32(kbd.size() - header_size)
    kbd.seek(score_pos)
    kbd.write_uint32(max_score)
    if cutscene_start:
        kbd.write_uint32(max_cutscene_score)

    with open(output_file, 'wb') as f:
        f.write(kbd.buffer())


def load_file(input_file, cutscene_start):
    output_file = f'{input_file}.kbd'
    import_to_kbd(input_file, output_file, cutscene_start)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.kbd)',
                        type=str, nargs='+')

    parser.add_argument("-css,", "--cutscenestart",
                        help="Calculates cutscene score using the cutscene start timing (seconds).", nargs='?', const=1, type=float)
    args = parser.parse_args()

    if args.cutscenestart:
        cutscene_start = args.cutscenestart
    else:
        cutscene_start = None

    input_files = args.input
    file_count = 0
    for file in input_files:
        load_file(file, cutscene_start)
        file_count += 1
    print(f'{file_count} file(s) converted.')
    os.system('pause')


if __name__ == "__main__":
    main()
