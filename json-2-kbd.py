from binary_reader import BinaryReader
import argparse
import json
import os

def get_button_type(button):
    if button == 'Circle':
        return 0
    elif button == 'Cross':
        return 1
    elif button == 'Square':
        return 2
    elif button == 'Triangle':
        return 3
    else:
        print(f'Invalid button {button}!')
        raise ValueError

def get_note_type(note):
    if note == 'Regular':
        return 0
    elif note == 'Hold':
        return 1
    elif note == 'Rapid':
        return 2
    else:
        print(f'Invalid note {note}!')
        raise ValueError

def export_to_json(input_file, output_file):
    with open(input_file) as f:
        data = json.loads(f.read())

    kbd = BinaryReader(bytearray())

    # HEADER

    kbd.write_str(data['Header']['Magic'])
    kbd.write_uint32(0)
    kbd.write_uint32(data['Header']['Version'])
    kbd.write_uint32(data['Header']['Size w/o header'])
    kbd.write_uint32(data['Header']['Note count'])
    kbd.write_uint32(data['Header']['Max score'])
    kbd.write_uint32(data['Header']['Unknown 1'])

    # NOTES
    i = 0
    while i < data['Header']['Note count']:
        note = data['Notes'][i]
        kbd.write_uint32(note['Start position'])
        kbd.write_uint32(note['End position'])
        kbd.write_uint32(note['Vertical position'])
        kbd.write_uint32(0)
        kbd.write_uint32(get_button_type(note['Button type']))
        kbd.write_uint32(get_note_type(note['Note type']))
        kbd.write_uint16(note['Cue ID'])
        kbd.write_uint16(note['Cuesheet ID'])
        kbd.write_uint32(0)
        i += 1


    with open(output_file, 'wb') as f:
        f.write(kbd.buffer())

def load_file(input_file):
    output_file = f'{input_file}.kbd'
    export_to_json(input_file, output_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.kbd)', type=str, nargs='+')
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