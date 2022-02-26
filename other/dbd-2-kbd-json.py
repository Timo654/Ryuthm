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
        return 'Triangle'
    elif button == 3:
        return 'Square'
    elif button == 4:
        return 'Unknown'
    elif button == 5:
        return 'All'
    else:
        return f'Unknown button {button}'

def convert_to_ms(position):
    if position != 0:
        return position / 3
    else:
        return 0

def read_pos(dbd, ms_mode):
    if ms_mode:
        return convert_to_ms(dbd.read_uint32())
    else:
        return dbd.read_uint32()

def get_line(button):
    if button == 'Triangle':
        return 0
    elif button == 'Square':
        return 2
    elif button == 'Circle':
        return 4
    elif button == 'Cross':
        return 6


def export_to_json(input_file, output_file, ms_mode):
    file = open(input_file, 'rb')
    dbd = BinaryReader(file.read())
    file.close()

    data = {}
    # HEADER

    data['Header'] = {}
    data['Header']['Magic'] = dbd.read_str(4)
    dbd.seek(4, 1)
    data['Header']['Version'] = dbd.read_uint32()
    dbd.seek(4, 1) #size w/o header
    data['Header']['Converted to milliseconds'] = ms_mode
    data['Header']['Note count'] = dbd.read_uint32()
    data['Header']['Unknown'] = dbd.read_uint32()
    data['Header']['Max score pre-cutscene'] = 0
    # NOTES
    note_list = []
    i = 1
    while i <= data['Header']['Note count']:
        note = {}
        note['Index'] = i
        note['Start position'] = read_pos(dbd, ms_mode)
        note['End position'] = read_pos(dbd, ms_mode)
        note['Button type'] = get_button_type(dbd.read_uint32())
        note['Vertical position'] = get_line(note['Button type'])
        if note['End position'] > 0:
            note['Note type'] = 'Hold'
        else:
            note['Note type'] = 'Regular'
        note['Cue ID'] = 0
        note['Cuesheet ID'] = 0
        note['Note type'] = dbd.read_uint32()
        dbd.seek(8, 1)
        if note['Button type'] not in ['Unknown', 'All']:
            note_list.append(note)
        i += 1

    data['Notes'] = note_list

    with open(output_file, 'w') as fp:
        json.dump(data, fp, indent=2)


def load_file(input_file, ms_mode):
    output_file = f'{input_file}.json'
    export_to_json(input_file, output_file, ms_mode)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.dbd)',
                        type=str, nargs='+')
    parser.add_argument("-noms,", "--nomilliseconds",
                        help="Doesn't convert position to milliseconds", nargs='?', const=1, type=int)
    args = parser.parse_args()

    input_files = args.input

    if args.nomilliseconds:
        ms_mode = False
    else:
        ms_mode = True
    file_count = 0
    for file in input_files:
        load_file(file, ms_mode)
        file_count += 1
    print(f'{file_count} file(s) converted.')
    os.system('pause')


if __name__ == "__main__":
    main()
