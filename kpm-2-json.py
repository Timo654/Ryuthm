from binary_reader import BinaryReader
import argparse
import json
import os

def export_to_json(input_file, output_file):
    file = open(input_file, 'rb')

    kpm = BinaryReader(file.read())
    file.close()

    data = {}
    # HEADER
    data['Header'] = {}
    data['Header']['Magic'] = kpm.read_str(4)
    kpm.seek(8, 1)
    data['Header']['File size w/o header'] = kpm.read_uint32()
    data['Header']['Parameter count'] = kpm.read_uint32()

    # PARAMS
    param_list = []
    i = 1
    while i <= data['Header']['Parameter count']:
        param = {}
        param['Index'] = i
        param['Great range (Before)'] = kpm.read_float()
        param['Good range (Before)'] = kpm.read_float()
        param['Great range (After)'] = kpm.read_float()
        param['Good range (After)'] = kpm.read_float()
        param['Great Hold percentage'] = kpm.read_float()
        param['Good Hold percentage'] = kpm.read_float()
        param['Great Rapid press'] = kpm.read_uint32()
        param['Good Rapid press'] = kpm.read_uint32()
        param['Scale'] = kpm.read_float()
        param['Cutscene start time'] = kpm.read_float()
        param_list.append(param)
        i += 1

    data['Parameters'] = param_list

    with open(output_file, 'w') as fp:
        json.dump(data, fp, indent=2)

def load_file(input_file):
    output_file = f'{input_file}.json'
    export_to_json(input_file, output_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help='Input file (.kpm)', type=str, nargs='+')
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