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

def get_texture_name(kar, pointer, prev_pos):
    kar.seek(pointer)
    texture_name = kar.read_str()
    kar.seek(prev_pos)
    return texture_name

def export_to_json(input_file, output_file):
    with open(input_file) as f:
        data = json.loads(f.read())

    kar = BinaryReader(bytearray(), True)

    # HEADER
    kar.write_str(data['Header']['Magic'])
    kar.write_uint16(int(data['Header']['Endian identifier'], 16))
    if data['Header']['Game'] == 'Yakuza 4':
        kar.write_uint8(data['Header']['Number of lines'])
        kar.write_uint8(data['Header']['Unknown 1'])
    else:
        kar.write_uint16(0)
    kar.write_uint32(data['Header']['Version'])
    kar.write_uint32(0)
    if data['Header']['Game'] == 'Yakuza 5':
        kar.write_uint8(data['Header']['Number of lines'])
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

    while i < data['Header']['Number of lines']:
        line = data['Lines'][i]
        kar.write_uint32(line['Vertical position'])
        note_pnt_pos = kar.pos()
        kar.write_uint32(0) #note section pointer
        kar.write_uint32(line['Note count'])
        note_pnt_pos_list.append(note_pnt_pos)
        
        settings_pnt_pos = kar.pos()
        kar.write_uint32(0) #settings pointer

        settings_pnt_pos_list.append(settings_pnt_pos)

        kar.write_uint32(line['Unknown 13'])
        texture_pnt_pos = kar.pos()
        kar.write_uint32(0) #texture name pointer
        texture_pnt_pos_list.append(texture_pnt_pos)
        
        kar.write_uint32(line['Texture length?'])
        kar.write_uint32(line['Line spawn'])
        kar.write_uint32(line['Line despawn'])
        if i < data['Header']['Number of lines'] - 1: #last line doesnt have it
            kar.write_uint32(line['Line page'])

        i += 1

    new_note_pnt_list = []
    new_settings_pnt_list = []
    new_texture_pnt_list = []

    i = 0
    while i < data['Header']['Number of lines']:
        #line settings
        settings = data['Lines'][i]['Settings']
        settings_pos = kar.pos()
        new_settings_pnt_list.append(settings_pos)
        kar.write_uint32(settings['Max notes'])
        kar.write_uint32(settings['Line start time (ms)'])
        kar.write_uint32(settings['Line end time (ms)'])
        #note settings
        o = 0
        note_pos = kar.pos()
        new_note_pnt_list.append(note_pos)
        while o < data['Lines'][i]['Note count']:
            note = data['Lines'][i]['Notes'][o]
            kar.write_uint32(note['Note type'])
            kar.write_float(note['Note position'])
            kar.write_uint32(note['Unknown 14'])
            kar.write_uint32(note['Button type'])
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
    #update pointers
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