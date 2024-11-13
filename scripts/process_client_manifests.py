import argparse
import os

from client_manifest_lib.index import ClientManifestsIndex


result_processors = []

def process_manifests(index, args):

    with open(args.manifest_fofn, 'r') as input_file:
        for line in input_file:
            line = line.strip()
            header_manifest_name, restofline = line.split(':', 1)
            filename_with_hash = restofline.replace('"', '')
            pretty_filename, hash = filename_with_hash.rsplit('.', 1)


            if os.path.exists(f'{args.manifest_file_dir}/{filename_with_hash}'):
                index.index_file(args.manifest_file_dir, pretty_filename, hash, filename_with_hash, header_manifest_name)

            # mfobj = CDNManifestZipFile(hash, pretty_filename, filename_with_hash)
            # cdn_manifest_obj.contains.add(mfobj)

def print_manifest_files(index, args):

    for manifest in index.cm_objs():
        output = []
        for zip_file in manifest.children:
            #output.append(zip_file.pretty_name)
            for file_entry in zip_file.contains:
                output.append(f"{file_entry.filename}\t{file_entry.compress_size}\t{file_entry.crc}\t{file_entry.comment}")
        
        with open(f'{args.output_dir}/manifest_files/{manifest.name}.txt', 'w') as output_file:
            for line in sorted(output):
                print(line, file=output_file)

def print_manifest_files_onefile(index, args):
    with open(f'{args.output_dir}/manifest_files.txt', 'w') as output_file:


        for mzf_obj in index.cmzf_objs():
            print(f"Manfest item {mzf_obj.hash}:", file=output_file)
            print(f"\tUsed in the following:", file=output_file)

            for parent in mzf_obj.parents:
                print(f"\t\t{mzf_obj.pretty_name} in {parent.name}", file=output_file)
        
            print("", file=output_file)

            print("\tContained files:", file=output_file)
            for child in index.cmzfe_objs(mzf_obj):
                print(f"\t\t{child.filename}\t{child.compress_size}\t{child.crc}\t{child.comment}", file=output_file)
        
            print("", file=output_file)
            print("", file=output_file)

def print_sourcemaps(index, args):
    with open(f'{args.output_dir}/sourcemaps.txt', 'w') as output_file:

        for mzf_obj in index.cmzf_objs():

            print_me = any(child.source_map is not None for child in index.cmzfe_objs(mzf_obj))

            if print_me:
                
                print(f"Manfest item {mzf_obj.hash}:", file=output_file)
                print(f"\tUsed in the following:", file=output_file)

                for parent in mzf_obj.parents:
                    print(f"\t\t{mzf_obj.pretty_name} in {parent.name}", file=output_file)
            
                print("", file=output_file)

                print("\tContained files:", file=output_file)
                for child in index.cmzfe_objs(mzf_obj):
                    if child.source_map is not None:
                        print(f"\t\t{child.filename}\t{child.source_map}", file=output_file)
            
                print("", file=output_file)
                print("", file=output_file)
 
def main():
    parser = argparse.ArgumentParser(
                prog='ProgramName',
                description='What the program does',
                epilog='Text at the bottom of help')
    
    parser.add_argument('manifest_fofn', help='file containing list of client filenames that were downloaded')
    parser.add_argument('manifest_file_dir', help='where downloaded files from the manifest were stored')
    parser.add_argument('output_dir', help='where to write output files')

    args = parser.parse_args()

    os.makedirs(f'{args.output_dir}/manifest_files', exist_ok=True)

    index = ClientManifestsIndex()

    process_manifests(index, args)
    print_manifest_files(index, args)
    #print_manifest_files_onefile(index, args)
    print_sourcemaps(index, args)


if __name__ == "__main__":
    main()