import argparse
import json
import os
from binary_reader import BinaryReader


def import_to_klc(input_file, output_file):
    with open(input_file) as f:
        data = json.loads(f.read())
    klc = BinaryReader(bytearray())

    # HEADER
    klc.write_str('CRLK')  # magic
    klc.write_uint64(0)
    klc.write_uint32(data['Header']['Unknown 1'])
    klc.write_uint32(len(data['Lyrics']))  # lyric count

    # NOTES
    i = 0
    while i < len(data['Lyrics']):
        lyric = data['Lyrics'][i]
        klc.write_float(lyric['Start timing'])
        klc.write_float(lyric['End timing'])
        klc.write_float(lyric['Appear timing'])
        klc.write_float(lyric['Disappear timing'])
        klc.write_uint32(lyric['Vertical position'])
        klc.write_uint32(0)
        i += 1

    with open(output_file, 'wb') as f:
        f.write(klc.buffer())


def load_file(input_file):
    output_file = f'{input_file}.klc'
    import_to_klc(input_file, output_file)


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
