import argparse
import json
import os
from binary_reader import BinaryReader


def get_note_type(note):
    if note == 0:
        return 'Regular'
    elif note == 1:
        return 'Rapid'
    elif note == 2:
        return 'Hold'
    else:
        print(f'Unknown note {note}')
        return f'Unknown note {note}'


def get_button_type(button):
    if button == 0:
        return 'Cross'
    elif button == 1:
        return 'Circle'
    elif button == 2:
        return 'Square'
    elif button == 3:
        return 'Triangle'
    elif button == 4:
        return 'Left Arrow'
    elif button == 5:
        return 'Right Arrow'
    elif button == 7:
        return 'Black circle'  # ???
    else:
        print(f'Unknown button {button}')
        return f'Unknown button {button}'


def get_notes(kar, note_count, game):
    note_list = []
    i = 1
    while i <= note_count:
        note = {}
        note['Index'] = i
        note['Note type'] = get_note_type(kar.read_uint32())
        note['Start position'] = kar.read_float()
        note['End position'] = kar.read_float()
        note['Button type'] = get_button_type(kar.read_uint32())
        note['Unknown 17'] = kar.read_uint32()
        note['Cuesheet ID'] = hex(kar.read_uint16())
        note['Cue ID'] = kar.read_uint16()
        if game != 'Yakuza 3':
            note['Unknown 18'] = kar.read_uint32()
        note_list.append(note)
        i += 1
    return note_list


def get_settings(kar):
    settings = {}
    settings['Line length'] = kar.read_uint32()
    settings['Line start time (ms)'] = kar.read_uint32()
    settings['Line end time (ms)'] = kar.read_uint32()
    return settings


def get_game(content):
    if content == 0:
        return 'Yakuza 5'
    else:
        return 'Yakuza 4'


def export_to_json(input_file, output_file, y3_mode):
    file = open(input_file, 'rb')
    kar = BinaryReader(file.read(), True)
    file.close()

    data = {}
    # HEADER
    data['Header'] = {}
    data['Header']['Magic'] = kar.read_str(4)
    kar.seek(2, 1) #endian identifier
    if y3_mode:
        data['Header']['Game'] = 'Yakuza 3'
    else:
        with kar.seek_to(0, 1):
            data['Header']['Game'] = get_game(kar.read_uint16())
            
    if data['Header']['Game'] in ['Yakuza 3', 'Yakuza 4']:
        data['Header']['Number of lines'] = kar.read_uint8()
        data['Header']['Unknown 1'] = kar.read_uint8()
    else:
        kar.seek(2, 1)
    data['Header']['Version'] = kar.read_uint32()

    kar.seek(4, 1)
    if data['Header']['Game'] == 'Yakuza 5':
        data['Header']['Number of lines'] = kar.read_uint8()
        data['Header']['Unknown 1'] = kar.read_uint8()
        kar.seek(14, 1)

    # MAIN TABLE
    data['Main table'] = {}
    data['Main table']['Unknown 2'] = kar.read_uint32()
    data['Main table']['Unknown 3'] = kar.read_uint32()
    data['Main table']['Notes for cutscene'] = kar.read_uint32()
    data['Main table']['Unknown 4'] = kar.read_uint32()
    data['Main table']['Unknown 5'] = kar.read_uint32()
    data['Main table']['Unknown 6'] = kar.read_uint32()
    data['Main table']['Unknown 7'] = kar.read_uint32()
    data['Main table']['Unknown 8'] = kar.read_uint32()
    data['Main table']['Unknown 9'] = kar.read_float()
    data['Main table']['Unknown 10'] = kar.read_float()
    data['Main table']['Unknown 11'] = kar.read_float()
    data['Main table']['Cheer difficulty'] = kar.read_uint32()
    data['Main table']['Unknown 12'] = kar.read_uint32()
    data['Main table']['Great range'] = kar.read_float()
    data['Main table']['Good range'] = kar.read_float()
    data['Main table']['Unknown 13'] = kar.read_uint32()

    # LINES
    line_list = []
    i = 1
    while i <= data['Header']['Number of lines']:
        line = {}
        line['Index'] = i
        line['Vertical position'] = kar.read_uint32()
        note_section_pointer = kar.read_uint32()
        line['Note count'] = kar.read_uint32()

        with kar.seek_to(note_section_pointer):
            line['Notes'] = get_notes(kar, line['Note count'], data['Header']['Game'])

        line_settings_pointer = kar.read_uint32()

        with kar.seek_to(line_settings_pointer):
            line['Settings'] = get_settings(kar)

        line['Unknown 14'] = kar.read_uint32()
        texture_name_pointer = kar.read_uint32()
        with kar.seek_to(texture_name_pointer):
            line['Texture name'] = kar.read_str()

        line['Unknown 15'] = kar.read_uint32()
        line['Line spawn'] = kar.read_uint32()
        line['Line despawn'] = kar.read_uint32()
        if i < data['Header']['Number of lines']:  # doesn't exist for last note
            line['Line page'] = kar.read_uint32()

        line_list.append(line)
        i += 1

    data['Lines'] = line_list

    with open(output_file, 'w') as fp:
        json.dump(data, fp, indent=2)


def load_file(input_file, y3_mode):
    output_file = f'{input_file}.json'
    export_to_json(input_file, output_file, y3_mode)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.bin)',
                        type=str, nargs='+')
    parser.add_argument("-y3,", "--yakuza3",
                        help="Yakuza 3 mode", nargs='?', const=1, type=int)
    args = parser.parse_args()

    input_files = args.input

    if args.yakuza3:
        y3_mode = True
    else:
        y3_mode = False

    file_count = 0
    for file in input_files:
        load_file(file, y3_mode)
        file_count += 1
    print(f'{file_count} file(s) converted.')
    os.system('pause')


if __name__ == "__main__":
    main()
