import argparse
import json
import os

def convert_to_sec(value):
    return value / 1000

def get_vert_pos(new_spawn, old_end):
    if old_end > new_spawn:
        print(f'old_end {old_end} and new spawn {new_spawn}')
        return 1
    else:
        return 0 

def import_to_kara(input_file, output_file):
    with open(input_file) as f:
        data = json.loads(f.read())
    kbd = {}

    # HEADER
    kbd['Header'] = {}
    kbd['Header']['Magic'] = "CRLK"
    kbd['Header']['Unknown 1'] = 44
    kbd['Header']['Lyric count'] = len(data['Lines'])
    
    i = 0
    lyrics_list = []
    prev_disappear = 0
    while i < len(data['Lines']):
        lyric = {}
        line = data['Lines'][i]
        if line['Texture name'] != 'lyric_dmmy.dds':
            lyric['Index'] = i + 1
            lyric['Start timing'] = convert_to_sec(line['Settings']['Line start time (ms)'])
            lyric['End timing'] = convert_to_sec(line['Settings']['Line end time (ms)'])
            lyric['Appear timing'] = convert_to_sec(data['Lines'][i - 1]['Settings']['Line end time (ms)'])
            lyric['Disappear timing'] = convert_to_sec(line['Settings']['Line end time (ms)'])
            if prev_disappear != 0:
                lyric['Vertical position'] = get_vert_pos(lyric['Appear timing'], prev_disappear)
            else:
                lyric['Vertical position'] = 0
            lyric['KARA texture name'] = line['Texture name']
            prev_disappear = lyric['Disappear timing']
            lyrics_list.append(lyric)
        i += 1
        
    kbd['Lyrics'] = lyrics_list
    with open(output_file, 'w') as fp:
        json.dump(kbd, fp, indent=2)


def load_file(input_file):
    output_file = f'{input_file}.klc.json'
    import_to_kara(input_file, output_file)


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
