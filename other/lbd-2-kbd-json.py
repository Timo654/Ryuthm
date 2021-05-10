import argparse
import json
import os
from binary_reader import BinaryReader

def get_line(button):
    if button == 'Triangle':
        return 0
    elif button == 'Square':
        return 2
    elif button == 'Circle':
        return 4
    elif button == 'Cross':
        return 6

def get_note_type(end_pos):
    if end_pos == 0:
        return 'Regular'
    else:
        return 'Hold'

def import_to_kara(input_file, output_file):
    with open(input_file) as f:
        data = json.loads(f.read())
    kbd = {}

    # HEADER
    kbd['Header'] = {}
    kbd['Header']['Magic'] = "NTBK"
    kbd['Header']['Version'] = 2
    kbd['Header']['Size w/o header'] = 0
    kbd['Header']['Converted to milliseconds'] = True
    kbd['Header']['Note count'] = 0
    kbd['Header']['Max score'] = 0
    kbd['Header']['Max score pre-cutscene'] = 0

    
    i = 0
    notes_list = []
    # update pointers
    while i < len(data['Notes']):
        oldnote = data['Notes'][i]
        if oldnote['Input type'] in ('Triangle', 'Circle', 'Square', 'Cross'): 
            newnote = {}
            newnote['Index'] = i + 1 #easier to see
            newnote['Start position'] = oldnote['Start timing']
            newnote['End position'] = oldnote['End timing']
            newnote['Vertical position'] = get_line(oldnote['Input type'])
            newnote['Button type'] = oldnote['Input type'] #fix bomb shit and other
            newnote['Note type'] = get_note_type(oldnote['End timing'])
            newnote['Cue ID'] = 0
            newnote['Cuesheet ID'] = 0
            notes_list.append(newnote)
            i += 1
        else:
            data['Notes'].pop(i)

    kbd['Notes'] = notes_list
    kbd['Header']['Note count'] = len(kbd['Notes']) #update header after note list was modified

    with open(output_file, 'w') as fp:
        json.dump(kbd, fp, indent=2)


def load_file(input_file):
    output_file = f'{input_file}.conv.json'
    import_to_kara(input_file, output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.lbd.json)',
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
