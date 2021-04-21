import argparse
import json
import os
from binary_reader import BinaryReader


def import_to_kpm(input_file, output_file):
    with open(input_file) as f:
        data = json.loads(f.read())
    kpm = BinaryReader(bytearray())

    # HEADER
    kpm.write_str(data['Header']['Magic'])
    kpm.write_uint32(0)
    kpm.write_uint32(data['Header']['Version'])
    size_pos = kpm.pos()
    kpm.write_uint32(0)  # size
    kpm.write_uint32(len(data['Parameters']))  # param count

    # PARAMS
    i = 0
    while i < len(data['Parameters']):
        param = data['Parameters'][i]
        kpm.write_float(param['Great range (Before)'])
        kpm.write_float(param['Good range (Before)'])
        kpm.write_float(param['Great range (After)'])
        kpm.write_float(param['Good range (After)'])
        kpm.write_float(param['Great Hold percentage'])
        kpm.write_float(param['Good Hold percentage'])
        kpm.write_uint32(param['Great Rapid press'])
        kpm.write_uint32(param['Good Rapid press'])
        kpm.write_float(param['Scale'])
        kpm.write_float(param['Cutscene start time'])
        if data['Header']['Version'] > 0:
            kpm.write_float(param['Unknown 1'])
        i += 1

    kpm.seek(size_pos)
    kpm.write_uint32(kpm.size() - 0x14)

    with open(output_file, 'wb') as f:
        f.write(kpm.buffer())


def load_file(input_file):
    output_file = f'{input_file}.kpm'
    import_to_kpm(input_file, output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.kpm)',
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
