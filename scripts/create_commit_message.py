import subprocess
import glob
import sys
import re
import os

name_filters = [
    re.compile(r'^bin/cef'),
    re.compile(r'Chromium Embedded Framework|localization|v8_context_snapshot|snapshot_blob'),
    re.compile(r'(\.pak|\.tga|\.svg|\.png|\.ico)$'),
]

def handle_diff_line__inner(line, sep, result_dict):
    if line[0] == sep:
        # handle plus
        if len(line) >= 3 and line[:3] == sep * 3:
            return
        try:
            name, size, _ = line[1:].split('\t', 2)
        except ValueError as e:
            print(e)
            print(line)
            raise
        
        for name_filter in name_filters:
            if len(name_filter.findall(name)) > 0:
                return
        
        result_dict[name] = int(size)

def handle_diff_line(line, added_dict, removed_dict):
    line = line.rstrip()
    if len(line) == 0:
        return
    handle_diff_line__inner(line, '+', added_dict)
    handle_diff_line__inner(line, '-', removed_dict)

def gen_dicts(manifest_filepath):

    added_dict = {}
    removed_dict = {}

    cmd = ['git', 'diff', '--unified=0', '--']
    cmd.append(manifest_filepath)

    try:
        result_raw = subprocess.check_output(cmd).decode('UTF-8').rstrip()
    except subprocess.CalledProcessError:
        print(f'git diff failed for {manifest_filepath}', file=sys.stderr)
        return added_dict, removed_dict

    if 'new file mode' in result_raw:
        # if the file was just created it's going to be a dump
        return added_dict, removed_dict

    if len(result_raw) > 0:
        for line in result_raw.split('\n'):
            handle_diff_line(line, added_dict, removed_dict)

    return added_dict, removed_dict
        
def compare(added_dict, removed_dict, summary_counts):

    result = []

    for key in added_dict:
        if key not in removed_dict:
            result.append(f"\tAdded file: {key}")
            summary_counts['added'] += 1

    for key in removed_dict:
        if key not in added_dict:
            result.append(f"\tRemoved file: {key}")
            summary_counts['removed'] += 1
        else:
            mag = added_dict[key] - removed_dict[key]
            pct = mag / removed_dict[key] * 100
            if mag > 0 and pct > 20:
                result.append(f"\tFile size delta: {key} : {removed_dict[key]} -> {added_dict[key]} ")
                summary_counts['delta'] += 1

    return result


def main():

    summary_counts = {
        'added': 0,
        'removed': 0,
        'delta': 0
    }

    results = {}

    for manifest_filepath in glob.glob('results/manifest_files/*.txt'):

        added_dict, removed_dict = gen_dicts(manifest_filepath)
        
        result = compare(added_dict, removed_dict, summary_counts)

        if len(result) > 0:
            results[manifest_filepath] = list(sorted(result))


    print(f"Client manifest update: {summary_counts['added']} added, {summary_counts['removed']} removed, {summary_counts['delta']} large delta")
    print()

    for manifest_filepath, result in results.items():
        if len(result) > 0:
            print(os.path.basename(manifest_filepath))
            print("\n".join(result))
        
if __name__ == '__main__':
    main()