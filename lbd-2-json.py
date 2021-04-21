import argparse
import json
import os
from binary_reader import BinaryReader


def get_button_type(button, version):
    if button == 0:
        return 'Circle'
    elif button == 1:
        return 'Cross'
    elif version > 2:  # Ishin and Yakuza 0
        if button == 2:
            return 'Triangle'
        elif button == 3:
            return 'Square'
        elif button == 4:
            return 'Right'
        elif button == 5:
            return 'Down'
        elif button == 6:
            return 'Up'
        elif button == 7:
            return 'Left'
        elif button == 8:
            return 'Countdown'
        elif button == 9:
            return 'Unk1'
        elif button == 10:
            return 'Unk2'
        elif button == 11:
            return 'End'
        else:
            print(f'{button}')
            return f'Unknown button {button}'
    else:  # Yakuza 5
        if button == 2:
            return 'Square'
        elif button == 3:
            return 'Triangle'
        elif button == 4:
            return 'Bomb'
        elif button == 9:
            return 'Up'
        elif button == 10:
            return 'Down'
        elif button == 11:
            return 'Right'
        elif button == 12:
            return 'Left'
        else:
            print(f'{button}')
            return f'Unknown button {button}'


def convert_to_ms(position):
    if position != 0:
        return position / 3
    else:
        return 0


def read_pos(lbd, ms_mode):
    if ms_mode:
        return convert_to_ms(lbd.read_uint32())
    else:
        return lbd.read_uint32()


def export_to_json(input_file, output_file, ms_mode):
    file = open(input_file, 'rb')
    lbd = BinaryReader(file.read(), True)
    file.close()

    data = {}
    # HEADER
    data['Header'] = {}
    data['Header']['Version'] = lbd.read_uint16()
    if data['Header']['Version'] == 0:
        data['Header']['Number of notes'] = lbd.read_uint16()
    else:
        lbd.seek(2, 1)
        data['Header']['Number of notes'] = lbd.read_uint32()
    data['Header']['Climax heat'] = bool(lbd.read_uint32())
    data['Header']['Converted to milliseconds'] = ms_mode
    data['Header']['Unknown 1'] = lbd.read_uint32()
    data['Header']['Hit Range (Before)'] = read_pos(lbd, ms_mode)
    data['Header']['Good Range (Before)'] = read_pos(lbd, ms_mode)
    data['Header']['Great Range (Before)'] = read_pos(lbd, ms_mode)
    data['Header']['Special Mode Start'] = read_pos(lbd, ms_mode)
    data['Header']['Special Mode Length'] = read_pos(lbd, ms_mode)
    if data['Header']['Version'] > 0:
        data['Header']['Scale'] = lbd.read_uint32()
        data['Header']['Good Range (After)'] = read_pos(lbd, ms_mode)
        data['Header']['Great Range (After)'] = read_pos(lbd, ms_mode)
        data['Header']['Hit Range (After)'] = read_pos(lbd, ms_mode)

    if data['Header']['Version'] > 3:
        lbd.seek(12, 1)  # padding

    # NOTES
    note_list = []
    i = 1
    while i <= data['Header']['Number of notes']:
        note = {}
        note['Index'] = i

        note['Unknown 2'] = lbd.read_uint8()
        note['Line'] = lbd.read_uint8()
        note['Unknown 3'] = lbd.read_uint8()
        note['Input type'] = get_button_type(
            lbd.read_uint8(), data['Header']['Version'])
        note['Start timing'] = read_pos(lbd, ms_mode)
        note['End timing'] = read_pos(lbd, ms_mode)

        if data['Header']['Version'] > 3:
            note['Grid position'] = lbd.read_uint32()
        note_list.append(note)
        i += 1

    data['Notes'] = note_list

    if data['Header']['Climax heat']:
        data['Header']['Costume Switch Start'] = read_pos(lbd, ms_mode)
        data['Header']['Costume Switch End'] = read_pos(lbd, ms_mode)

    with open(output_file, 'w') as fp:
        json.dump(data, fp, indent=2)


def load_file(input_file, ms_mode):
    output_file = f'{input_file}.json'
    export_to_json(input_file, output_file, ms_mode)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.lbd)',
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
