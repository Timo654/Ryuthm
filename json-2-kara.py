import argparse
import json
import os
from binary_reader import BinaryReader


def get_note_type(note):
    if note == 'regular':
        return 0
    elif note == 'rapid':
        return 1
    elif note == 'hold':
        return 2
    else:
        print(f'Unknown note {note}!')
        raise ValueError


def get_button_type(button):
    if button == 'cross':
        return 0
    elif button == 'circle':
        return 1
    elif button == 'square':
        return 2
    elif button == 'triangle':
        return 3
    elif button == 'left arrow':
        return 4
    elif button == 'right arrow':
        return 5
    elif button == 'black circle':  # ???
        return 7
    else:
        print(f'Unknown button {button}')
        return f'Unknown button {button}'


def import_to_kara(input_file, output_file):
    with open(input_file) as f:
        data = json.loads(f.read())
    kar = BinaryReader(bytearray(), True)

    # HEADER
    kar.write_str('KARA')  # magic
    kar.write_uint16(0x201)  # endian identifier
    if data['Header']['Game'] == 'Yakuza 4':
        kar.write_uint8(len(data['Lines']))
        kar.write_uint8(data['Header']['Unknown 1'])
    else:
        kar.write_uint16(0)
    kar.write_uint32(data['Header']['Version'])
    kar.write_uint32(0)
    if data['Header']['Game'] == 'Yakuza 5':
        kar.write_uint8(len(data['Lines']))
        kar.write_uint8(data['Header']['Unknown 1'])
        kar.write_uint16(0)
        kar.write_uint32(0)
        kar.write_uint32(0)
        kar.write_uint32(0)

    # MAIN TABLE
    kar.write_uint32(data['Main table']['Unknown 2'])
    kar.write_uint32(data['Main table']['Unknown 3'])
    kar.write_uint32(data['Main table']['Notes for cutscene'])
    kar.write_uint32(data['Main table']['Unknown 4'])
    kar.write_uint32(data['Main table']['Unknown 5'])
    kar.write_uint32(data['Main table']['Unknown 6'])
    kar.write_uint32(data['Main table']['Unknown 7'])
    kar.write_uint32(data['Main table']['Unknown 8'])
    kar.write_float(data['Main table']['Unknown 9'])
    kar.write_float(data['Main table']['Unknown 10'])
    kar.write_float(data['Main table']['Unknown 11'])
    kar.write_uint32(data['Main table']['Cheer difficulty'])
    kar.write_uint32(data['Main table']['Unknown 12'])
    kar.write_float(data['Main table']['Great range'])
    kar.write_float(data['Main table']['Good range'])
    kar.write_uint32(0)

    # LINES
    i = 0
    note_pnt_pos_list = []
    settings_pnt_pos_list = []
    texture_pnt_pos_list = []

    while i < len(data['Lines']):
        line = data['Lines'][i]
        kar.write_uint32(line['Vertical position'])
        note_pnt_pos = kar.pos()
        kar.write_uint32(0)  # note section pointer
        kar.write_uint32(len(line['Notes']))  # note count
        note_pnt_pos_list.append(note_pnt_pos)

        settings_pnt_pos = kar.pos()
        kar.write_uint32(0)  # settings pointer

        settings_pnt_pos_list.append(settings_pnt_pos)

        kar.write_uint32(line['Unknown 13'])
        texture_pnt_pos = kar.pos()
        kar.write_uint32(0)  # texture name pointer
        texture_pnt_pos_list.append(texture_pnt_pos)

        kar.write_uint32(line['Texture length?'])
        kar.write_uint32(line['Line spawn'])
        kar.write_uint32(line['Line despawn'])
        if i < data['Header']['Number of lines'] - 1:  # last line doesnt have it
            kar.write_uint32(line['Line page'])

        i += 1

    new_note_pnt_list = []
    new_settings_pnt_list = []
    new_texture_pnt_list = []

    i = 0
    while i < len(data['Lines']):
        # line settings
        settings = data['Lines'][i]['Settings']
        settings_pos = kar.pos()
        new_settings_pnt_list.append(settings_pos)
        kar.write_uint32(settings['Max notes'])
        kar.write_uint32(settings['Line start time (ms)'])
        kar.write_uint32(settings['Line end time (ms)'])
        # note settings
        o = 0
        note_pos = kar.pos()
        new_note_pnt_list.append(note_pos)

        while o < len(data['Lines'][i]['Notes']):
            note = data['Lines'][i]['Notes'][o]
            kar.write_uint32(get_note_type(note['Note type'].lower()))
            kar.write_float(note['Note position'])
            kar.write_uint32(note['Unknown 14'])
            kar.write_uint32(get_button_type(note['Button type'].lower()))
            kar.write_uint32(note['Unknown 15'])
            kar.write_uint16(int(note['Cuesheet ID'], 16))
            kar.write_uint16(note['Cue ID'])
            kar.write_uint32(note['Unknown 16'])
            o += 1

        texture_pos = kar.pos()
        new_texture_pnt_list.append(texture_pos)
        kar.write_str(data['Lines'][i]['Texture name'])
        kar.align(0x4)

        if data['Lines'][i]['Texture name'] != "lyric_dmmy.dds":
            kar.write_uint32(0)
            kar.write_uint32(0)
            if data['Header']['Game'] == 'Yakuza 4':
                kar.write_uint32(0)

        i += 1

    i = 0
    # update pointers
    while i < len(new_note_pnt_list):
        kar.seek(note_pnt_pos_list[i])
        kar.write_uint32(new_note_pnt_list[i])

        kar.seek(settings_pnt_pos_list[i])
        kar.write_uint32(new_settings_pnt_list[i])

        kar.seek(texture_pnt_pos_list[i])
        kar.write_uint32(new_texture_pnt_list[i])

        i += 1

    with open(output_file, 'wb') as f:
        f.write(kar.buffer())


def load_file(input_file):
    output_file = f'{input_file}.bin'
    import_to_kara(input_file, output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.bin)',
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
