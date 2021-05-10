import argparse
import json
import os
from binary_reader import BinaryReader


def get_button_type(button):
    if button == 0:
        return 'Cross'
    elif button == 1:
        return 'Circle'
    elif button == 2:
        return 'Square'
    elif button == 3:
        return 'Triangle'


def export_to_json(input_file, output_file):
    file = open(input_file, 'rb')
    wtfl = BinaryReader(file.read(), True)
    file.close()

    data = {}
    # HEADER
    data['Header'] = {}
    data['Header']['Magic'] = wtfl.read_str(4)
    wtfl.seek(4, 1) #endian check
    data['Header']['Number of notes'] = wtfl.read_uint8()
    data['Header']['Unknown 1'] = wtfl.read_uint8()
    data['Header']['Version'] = hex(wtfl.read_uint32())
    wtfl.seek(4, 1)
    if int(data['Header']['Version'], 16) > 0x1000000:
        data['Header']['Stage'] = wtfl.read_str(13)

    # NOTES
    note_list = []
    i = 1
    while i <= data['Header']['Number of notes']:
        note = {}
        note['Index'] = i
        note['Button type'] = get_button_type(wtfl.read_uint32())
        note['Position'] = wtfl.read_float()
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
    parser.add_argument("input",  help='Input file (.wtfl)',
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
