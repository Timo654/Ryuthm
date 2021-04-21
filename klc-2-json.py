import argparse
import json
import os
from binary_reader import BinaryReader


def export_to_json(input_file, output_file):
    file = open(input_file, 'rb')
    klc = BinaryReader(file.read())
    file.close()

    data = {}
    # HEADER
    data['Header'] = {}
    data['Header']['Magic'] = klc.read_str(4)
    klc.seek(8, 1)
    data['Header']['Unknown 1'] = klc.read_uint32()
    data['Header']['Lyric count'] = klc.read_uint32()

    # NOTES
    lyric_list = []
    i = 1
    while i <= data['Header']['Lyric count']:
        lyric = {}
        lyric['Index'] = i
        lyric['Start timing'] = klc.read_float()
        lyric['End timing'] = klc.read_float()
        lyric['Appear timing'] = klc.read_float()
        lyric['Timing timing'] = klc.read_float()
        lyric['Vertical position'] = klc.read_uint32()
        klc.seek(4, 1)
        lyric_list.append(lyric)
        i += 1

    data['Lyrics'] = lyric_list

    with open(output_file, 'w') as fp:
        json.dump(data, fp, indent=2)


def load_file(input_file):
    output_file = f'{input_file}.json'
    export_to_json(input_file, output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.klc)',
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
