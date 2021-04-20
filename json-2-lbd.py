from binary_reader import BinaryReader
import argparse
import json
import sys
import os

def get_button_type(button, version):
    if button == 'Circle':
        return 0
    elif button == 'Cross':
        return 1
    elif version > 2: #Ishin and Yakuza 0
        if button == 'Triangle':
            return 2
        elif button == 'Square':
            return 3
        elif button == 'Right':
            return 4
        elif button == 'Down':
            return 5
        elif button == 'Up':
            return 6
        elif button == 'Left':
            return 7
        elif button == 'Countdown':
            return 8
        elif button == 'Unk1':
            return 9
        elif button == 'Unk2':
            return 10
        elif button == 'End':
            return 11
        else:
            print(f'Invalid button {button}!')
            raise ValueError
    else: #Yakuza 5
        if button == 'Square':
            return 2
        elif button == 'Triangle':
            return 3
        elif button == 'Bomb':
            return 4
        elif button == 'Up':
            return 9
        elif button == 'Down':
            return 10
        elif button == 'Right':
            return 11
        elif button == 'Left':
            return 12
        else:
            print(f'Invalid button {button}!')
            raise ValueError

def convert_to_pos(ms):
    if ms != 0:
        return int(ms * 3)
    else:
        return 0
        
def write_pos(lbd, content, ms_mode):
    if ms_mode:
        lbd.write_uint32(convert_to_pos(content))
    else:
        lbd.write_uint32(content)

def import_to_kbd(input_file, output_file):
    with open(input_file) as f:
        data = json.loads(f.read())

    lbd = BinaryReader(bytearray())
    lbd.set_endian(True)

    # HEADER
    lbd.write_uint16(data['Header']['Version'])
    if data['Header']['Version'] == 0:
        lbd.write_uint16(len(data['Notes']))
    else:
        lbd.write_uint16(0xFFFF)
        lbd.write_uint32(len(data['Notes']))
    lbd.write_uint32(data['Header']['Climax heat'])
    ms_mode = data['Header']['Converted to milliseconds']
    lbd.write_uint32(data['Header']['Unknown 1'])
    write_pos(lbd, data['Header']['Hit Range (Before)'], ms_mode)
    write_pos(lbd, data['Header']['Good Range (Before)'], ms_mode)
    write_pos(lbd, data['Header']['Great Range (Before)'], ms_mode)
    write_pos(lbd, data['Header']['Special Mode Start'], ms_mode)
    write_pos(lbd, data['Header']['Special Mode Length'], ms_mode)
    if data['Header']['Version'] > 0:
        lbd.write_uint32(data['Header']['Scale'])
        write_pos(lbd, data['Header']['Good Range (After)'], ms_mode)
        write_pos(lbd, data['Header']['Great Range (After)'], ms_mode)
        write_pos(lbd, data['Header']['Hit Range (After)'], ms_mode)

    if data['Header']['Version'] > 3:
        lbd.write_uint32(0)
        lbd.write_uint32(0)
        lbd.write_uint32(0)
    
    # NOTES
    i = 0
    while i < len(data['Notes']):
        note = data['Notes'][i]
        lbd.write_uint8(note['Unknown 2'])
        lbd.write_uint8(note['Line'])
        lbd.write_uint8(note['Unknown 3'])
        lbd.write_uint8(get_button_type(note['Button type'], data['Header']['Version']))
        write_pos(lbd, note['Start position'], ms_mode)
        write_pos(lbd, note['End position'], ms_mode)

        if data['Header']['Version'] > 3:
            lbd.write_uint32(note['Grid position'])
        i += 1


    if data['Header']['Climax heat']:
        write_pos(lbd, data['Header']['Costume Switch Start'], ms_mode)
        write_pos(lbd, data['Header']['Costume Switch End'], ms_mode)
    
    with open(output_file, 'wb') as f:
        f.write(lbd.buffer())

def load_file(input_file):
    output_file = f'{input_file}.lbd'
    import_to_kbd(input_file, output_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.lbd)', type=str, nargs='+')
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