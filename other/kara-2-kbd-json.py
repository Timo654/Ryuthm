import argparse
import json
import os

def get_line(button):
    if button == 'Triangle':
        return 0
    elif button == 'Square':
        return 2
    elif button == 'Circle':
        return 4
    elif button == 'Cross':
        return 6
    elif button == 'Left Arrow':
        return 2
    elif button == 'Right Arrow':
        return 4

def get_button(button):
    if button == 'Left Arrow':
        return 'Circle'
    elif button == 'Right Arrow':
        return 'Square'
    else:
        return button
    
def convert_to_kbd(input_file, output_file):
    with open(input_file) as f:
        data = json.loads(f.read())
    kbd = {}

    # HEADER
    kbd['Header'] = {}
    kbd['Header']['Magic'] = "NTBK"
    kbd['Header']['Version'] = 2
    kbd['Header']['Converted to milliseconds'] = True
    kbd['Header']['Note count'] = 0
    kbd['Header']['Max score'] = 0 
    kbd['Header']['Max score pre-cutscene'] = 0

    # LINES
    i = 0
    note_s_pos_list = []
    note_e_pos_list = []
    button_type_list = []
    note_type_list = []
    cuesheet_list = []
    cue_list = []
    
    i = 0
    while i < len(data['Lines']):
        o = 0
        while o < len(data['Lines'][i]['Notes']):
            note = data['Lines'][i]['Notes'][o]

        
            #If Unknown 15 is 0, Line length has to be divided by 2 to get the max percentage, otherwise it has to be divided by 24.
            if not data['Lines'][i]['Unknown 15']:
                max_percent = data['Lines'][i]['Settings']['Line length'] / 2
            else: 
                max_percent = data['Lines'][i]['Settings']['Line length'] / 24 

            #To get the actual start and end (relative to current line) percentage of a note, divide the "Start Position" by max percentage
            start_pos =  note['Start position'] / max_percent
            end_pos = note['End position'] / max_percent

            #Calculating line length (milliseconds) by subtracting start time from end time
            line_length = data['Lines'][i]['Settings']['Line end time (ms)'] - data['Lines'][i]['Settings']['Line start time (ms)']
            #Calculating the actual start pos of a note by multiplying the line length with the start pos percentage and then adding that to the line start time. (milliseconds)
            actual_s_pos = data['Lines'][i]['Settings']['Line start time (ms)'] + (line_length * start_pos)

            note_s_pos_list.append(actual_s_pos)
            if note['End position'] > 0:  
                actual_e_pos = data['Lines'][i]['Settings']['Line start time (ms)'] + (line_length * end_pos)
            else:
                actual_e_pos = 0 
            note_e_pos_list.append(actual_e_pos)
            button_type_list.append(note['Button type'])
            note_type_list.append(note['Note type'])
            cuesheet_list.append(note['Cuesheet ID'])
            cue_list.append(note['Cue ID'])
            o += 1


        i += 1

    i = 0
    notes_list = []
    # update pointers
    while i < len(note_s_pos_list):
        newnote = {}
        newnote['Index'] = i
        newnote['Start position'] = note_s_pos_list[i]
        newnote['End position'] = note_e_pos_list[i]
        newnote['Vertical position'] = get_line(button_type_list[i])
        newnote['Button type'] = get_button(button_type_list[i])
        newnote['Note type'] = note_type_list[i]
        newnote['Cue ID'] = 0
        newnote['Cuesheet ID'] = 0
        newnote['KARA Cue ID'] = cue_list[i]
        newnote['KARA Cuesheet ID'] = cuesheet_list[i]
        notes_list.append(newnote)

        i += 1
    kbd['Notes'] = notes_list
    with open(output_file, 'w') as fp:
        json.dump(kbd, fp, indent=2)


def load_file(input_file):
    output_file = f'{input_file}.kbd.json'
    convert_to_kbd(input_file, output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.bin.json)',
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
