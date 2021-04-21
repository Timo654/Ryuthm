import argparse
import json
import os
from binary_reader import BinaryReader


def get_button_type(button):
    if button == 0:
        return 'Circle'
    elif button == 1:
        return 'Cross'
    elif button == 2:
        return 'Square'
    elif button == 3:
        return 'Triangle'
    else:
        return f'Unknown button {button}'


def get_note_type(note):
    if note == 0:
        return 'Regular'
    elif note == 1:
        return 'Hold'
    elif note == 2:
        return 'Rapid'
    else:
        return f'Unknown note {note}'


def export_to_json(input_file, output_file):
    file = open(input_file, 'rb')
    kbd = BinaryReader(file.read())
    file.close()

    data = {}
    # HEADER
    data['Header'] = {}
    data['Header']['Magic'] = kbd.read_str(4)
    kbd.seek(4, 1)
    data['Header']['Version'] = kbd.read_uint32()
    data['Header']['Size w/o header'] = kbd.read_uint32()
    data['Header']['Note count'] = kbd.read_uint32()
    data['Header']['Max score'] = kbd.read_uint32()
    if data['Header']['Version'] > 1:
        data['Header']['Unknown 1'] = kbd.read_uint32()

    # NOTES
    note_list = []
    i = 1
    while i <= data['Header']['Note count']:
        note = {}
        note['Index'] = i
        note['Start position'] = kbd.read_uint32()
        note['End position'] = kbd.read_uint32()
        note['Vertical position'] = kbd.read_uint32()
        kbd.seek(4, 1)
        note['Button type'] = get_button_type(kbd.read_uint32())
        note['Note type'] = get_note_type(kbd.read_uint32())
        note['Cue ID'] = kbd.read_uint16()
        note['Cuesheet ID'] = kbd.read_uint16()
        kbd.seek(4, 1)
        note_list.append(note)
        i += 1

    data['Notes'] = note_list

    with open(output_file, 'w') as fp:
        json.dump(data, fp, indent=2)


def load_file(input_file):
    output_file = f'{input_file}.json'
    export_to_json(input_file, output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.kbd)',
                        type=str, nargs='+')
    args = parser.parse_args()
    input_files = args.input

    file_count = 0
    for file in input_files:
        load_file(file)
        file_count += 1
    print(f'{file_count} file(s) converted.')
    os.system('pause')


if __name__ == "__main__":
    main()
