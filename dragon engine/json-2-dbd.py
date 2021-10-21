import argparse
import json
import os
from binary_reader import BinaryReader


def get_button_type(button):
    if button == 'Circle':
        return 0
    elif button == 'Cross':
        return 1
    elif button == 'Triangle':
        return 2
    elif button == 'Square':
        return 3
    else:
        print(f'Invalid button {button}!')
        raise ValueError

def convert_to_pos(ms):
    if ms != 0:
        return int(ms * 3)
    else:
        return 0


def write_pos(dbd, content, ms_mode):
    if ms_mode:
        dbd.write_uint32(convert_to_pos(content))
    else:
        dbd.write_uint32(content)

def import_to_dbd(input_file, output_file, cutscene_start):
    with open(input_file) as f:
        data = json.loads(f.read())
    dbd = BinaryReader(bytearray())

    # HEADER
    dbd.write_str('NTBD')  # magic
    dbd.write_uint32(0)
    dbd.write_uint32(data['Header']['Version'])
    size_pos = dbd.pos()
    dbd.write_uint32(0)  # size
    dbd.write_uint32(len(data['Notes']))
    score_pos = dbd.pos()
    dbd.write_uint32(data['Header']["Unknown"])  # unknown
    ms_mode = data['Header']['Converted to milliseconds']

    # NOTES
    i = 0
    while i < len(data['Notes']):
        note = data['Notes'][i]
        write_pos(dbd, note['Start position'], ms_mode)
        write_pos(dbd, note['End position'], ms_mode)
        dbd.write_uint32(get_button_type(note['Button type']))
        dbd.write_uint32(note['Unknown'])
        dbd.write_uint32(note['Unknown 2'])
        dbd.write_uint32(0)

        i += 1

    dbd.seek(size_pos)

    header_size = 0x18

    dbd.write_uint32(dbd.size() - header_size)

    with open(output_file, 'wb') as f:
        f.write(dbd.buffer())


def load_file(input_file, cutscene_start):
    output_file = f'{input_file}.dbd'
    import_to_dbd(input_file, output_file, cutscene_start)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.dbd)',
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
