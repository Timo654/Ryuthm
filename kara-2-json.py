from binary_reader import BinaryReader
import argparse
import json
import os

def get_notes(kar, pointer, note_count, prev_pos):
    note_list = []
    kar.seek(pointer)
    i = 1
    while i <= note_count:
        note = {}
        note['Index'] = i
        note['Note type'] = kar.read_uint32()
        note['Note position'] = kar.read_float()
        note['Unknown 14'] = kar.read_uint32()
        note['Button type'] = kar.read_uint32()
        note['Unknown 15'] = kar.read_uint32()
        note['Cuesheet ID'] = hex(kar.read_uint16())
        note['Cue ID'] = kar.read_uint16()
        note['Unknown 16'] = kar.read_uint32()
        note_list.append(note)
        i += 1
    kar.seek(prev_pos)
    return note_list

def get_settings(kar, pointer, prev_pos):
    settings = {}
    kar.seek(pointer)
    settings['Max notes'] = kar.read_uint32()
    settings['Line start time (ms)'] = kar.read_uint32()
    settings['Line end time (ms)'] = kar.read_uint32()
    kar.seek(prev_pos)
    return settings

def get_texture_name(kar, pointer, prev_pos):
    kar.seek(pointer)
    texture_name = kar.read_str()
    kar.seek(prev_pos)
    return texture_name

def get_game(content):
    if content == 0:
        return 'Yakuza 5'
    else:
        return 'Yakuza 4'

def export_to_json(input_file, output_file):
    file = open(input_file, 'rb')

    kar = BinaryReader(file.read(), True)
    file.close()

    data = {}
    # HEADER
    data['Header'] = {}
    data['Header']['Magic'] = kar.read_str(4)
    data['Header']['Endian identifier'] = hex(kar.read_uint16())
    data['Header']['Game'] = get_game(kar.read_uint16())
    if data['Header']['Game'] == 'Yakuza 4':
        kar.seek(6)
        data['Header']['Number of lines'] = kar.read_uint8()
        data['Header']['Unknown 1'] = kar.read_uint8()
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
    kar.seek(4, 1)

    # LINES
    line_list = []
    i = 1
    while i <= data['Header']['Number of lines']:
        line = {}
        line['Index'] = i
        line['Vertical position'] = kar.read_uint32()
        note_section_pointer = kar.read_uint32()
        line['Note count'] = kar.read_uint32()
        notecount_pos = kar.pos()

        line['Notes'] = get_notes(kar, note_section_pointer, line['Note count'], notecount_pos)
        
        line_settings_pointer = kar.read_uint32()

        line_settings_pos = kar.pos()

        line['Settings'] = get_settings(kar, line_settings_pointer, line_settings_pos)

        line['Unknown 13'] = kar.read_uint32()
        texture_name_pointer = kar.read_uint32() #TODO - go to texture name
        tex_name_pos = kar.pos()
        line['Texture name'] = get_texture_name(kar, texture_name_pointer, tex_name_pos)

        line['Texture length?'] = kar.read_uint32()
        line['Line spawn'] = kar.read_uint32()
        line['Line despawn'] = kar.read_uint32()
        if i < data['Header']['Number of lines']: #doesn't exist for last note
            line['Line page'] = kar.read_uint32()   



        line_list.append(line)
        i += 1

    data['Lines'] = line_list

    with open(output_file, 'w') as fp:
        json.dump(data, fp, indent=2)


def load_file(input_file):
    output_file = f'{input_file}.json'
    export_to_json(input_file, output_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.bin)', type=str, nargs='+')
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