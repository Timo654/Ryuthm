import argparse
import json
import os
from binary_reader import BinaryReader


def get_button_type(button):
    if button == 0: #Down
        return 'Cross'
    elif button == 1:
        return 'Cross'
    elif button == 2: #Left
        return 'Square'
    elif button == 3:
        return 'Circle'
    elif button == 4: #Up
        return 'Triangle'
    elif button == 5:
        return 'Triangle'
    elif button == 8: #Scratch
        return 'Circle'
    else:
        print(f'{button}')
        return f'Unknown button {button}'

def get_line(button):
    if button == 0:
        return 3
    elif button == 1:
        return 0
    elif button == 2:
        return 2
    elif button == 3:
        return 1
    elif button == 4:
        return 2
    elif button == 5:
        return 3
    elif button == 8:
        return 1
    else:
        print(f'{button}')
        return f'Unknown button {button}'

def byPos(note):
    return note["Start timing"]

def sort_notes(note_list):
    note_list.sort(key=byPos)
    i = 0
    prev_start_pos = 0
    prev_end_pos = 0
    while i < len(note_list):
        note = note_list[i]
        if prev_end_pos != 0:
            if prev_start_pos <= note['Start timing'] <= prev_end_pos:
                note_list.pop(i)
            else:
                note['Index'] = i + 1 #so it wouldn't start from 0
                prev_start_pos = note['Start timing']
                prev_end_pos = note['End timing']
                i += 1    
        else:
            if note['Start timing'] == prev_start_pos:
                note_list.pop(i)
            else:
                note['Index'] = i + 1 #so it wouldn't start from 0
                prev_start_pos = note['Start timing']
                prev_end_pos = note['End timing']
                i += 1 

    return note_list

def export_to_json(input_file, output_file):
    file = open(input_file, 'rb')
    mns = BinaryReader(file.read())
    file.close()

    data = {}
    # HEADER
    mns.seek(16, 1)
    bpm = mns.read_float()
    bps = bpm / 60
    mns.seek(16, 1)

    actual_note_count = int((mns.size() - 36) / 8)

    data['Header'] = {}
    data['Header']['Version'] = 2
    data['Header']['Number of notes'] = actual_note_count
    data['Header']['Climax heat'] = False
    data['Header']['Converted to milliseconds'] = True
    data['Header']['Unknown 1'] = 145


    data['Header']['Hit Range (Before)'] = 300.0
    data['Header']['Good Range (Before)'] = 200.0
    data['Header']['Great Range (Before)'] = 100.0
    data['Header']['Special Mode Start'] = 0
    data['Header']['Special Mode Length'] = 0
    data['Header']['Scale'] = 9000
    data['Header']['Good Range (After)'] = 200.0
    data['Header']['Great Range (After)'] = 100.0
    data['Header']['Hit Range (After)'] = 300.0



    # NOTES
    note_list = []
    i = 1
    half = 0x8000
    while i <= actual_note_count:
        note = {}
        

        beat = mns.read_uint16()
        measure = mns.read_uint16()
        button = mns.read_uint8()
        hold_duration = mns.read_uint8()
        mns.seek(2, 1)
        beat_decimal = beat
        if ( beat & half ):
            beat_decimal = ( beat & ~half ) + 0.5

        total_seconds = (( measure * 4 ) + beat_decimal ) * ( 60.0 / bpm)
        total_ms = total_seconds * 1000

        note['Index'] = i
        note['Unknown 2'] = 0
        note['Line'] = get_line(button)
        note['Unknown 3'] = 0
        note['Input type'] = get_button_type(button)
        note['Start timing'] = total_ms
        if hold_duration:
            note['End timing'] = total_ms + (((hold_duration / 4 ) / bps) * 500) #might not be accurate, but it works well enough
        else:
            note['End timing'] = 0
        note_list.append(note)
        i += 1

    sort_notes(note_list)
    data['Notes'] = note_list
    data['Header']['Number of notes'] = len(data['Notes'])

    with open(output_file, 'w') as fp:
        json.dump(data, fp, indent=2)

def load_file(input_file):
    file = open(input_file, 'rb')
    mns = BinaryReader(file.read())
    file.close()
    try:
        if mns.read_str(4) == 'MNS':
            output_file = f'{input_file}.json'
            export_to_json(input_file, output_file)
        else:
            print('Invalid magic, skipping file.')
            return False
    except:
        print('Unable to read magic, skipping.')
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (mns***_*.bin)',
                        type=str, nargs='+')
    args = parser.parse_args()

    input_files = args.input

    file_count = 0
    for file in input_files:
        if load_file(file) != False: #in case invalid magic or exception
            file_count += 1
    print(f'{file_count} file(s) converted.')
    os.system('pause')


if __name__ == "__main__":
    main()
