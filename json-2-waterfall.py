from binary_reader import BinaryReader
import argparse
import json
import sys
import os

def get_button_type(button):
    if button == 'Cross':
        return 0
    elif button == 'Circle':
        return 1
    elif button == 'Square':
        return 2
    elif button == 'Triangle':
        return 3
        
def import_to_wtfl(input_file, output_file):
    with open(input_file) as f:
        data = json.loads(f.read())

    wtfl = BinaryReader(bytearray(), True)


    # HEADER
    wtfl.write_str(data['Header']['Magic'])
    wtfl.write_uint16(int(data['Header']['Endian check'], 16))
    wtfl.write_uint8(len(data['Notes']))
    wtfl.write_uint8(data['Header']['Unknown 1'])
    wtfl.write_uint32(int(data['Header']['Version'], 16))
    wtfl.write_uint32(0)
    if int(data['Header']['Version'], 16) > 0x1000000:
        wtfl.write_str(data['Header']['Stage'])

    # NOTES
    i = 0
    while i < len(data['Notes']):
        note = data['Notes'][i]
        wtfl.write_uint32(get_button_type(note['Button type']))
        wtfl.write_float(note['Position'])
        i += 1

    with open(output_file, 'wb') as f:
        f.write(wtfl.buffer())

def load_file(input_file):
    output_file = f'{input_file}.wtfl'
    import_to_wtfl(input_file, output_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.wtfl)', type=str, nargs='+')
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