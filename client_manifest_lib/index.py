import re
from .types import CDNClientManifest, ClientManifestZipFile, ClientManifestZipFileEntry, ResultFilter
from zipfile import ZipFile, BadZipFile
import re
import os

sourcemap_pattern = re.compile(rb'(?P<sourceMap>sourceMappingURL.{10,500})')

class ClientManifestsIndex:

    def __init__(self):
        # filename trailing hash -> ManifestFile
        self.map_clientmanifestzipfile_hash_to_object = {}
        self.map_cdnclientmanifest_name_to_obj = {}
    
    def index_file(self, manifest_file_dir, pretty_filename, hash, filename_with_hash, header_manifest_name):
        cmzf_obj = self.cmz_by_hash(hash, pretty_filename, filename_with_hash)
        cdn_manifest_obj = self.cm_by_name(header_manifest_name)
        cmzf_obj.parents.append(cdn_manifest_obj)
        cdn_manifest_obj.children.append(cmzf_obj)
        self.add_zip_file(cmzf_obj, f'{manifest_file_dir}/{filename_with_hash}')

    # zip files
    def add_zip_file(self, cdm_manifest_zip_file: ClientManifestZipFile, fpath):
        
        if len(cdm_manifest_zip_file.contains) > 0:
            return

        try:
            with ZipFile(fpath, 'r') as input_zip_file:

                for info in input_zip_file.infolist():

                    if info.is_dir():
                        continue

                    source_map = None

                    look_for_source_map = True

                    if info.filename.endswith('Chromium Embedded Framework'):
                        look_for_source_map = False

                    split_name = os.path.basename(info.filename).rsplit('.', 1)

                    if len(split_name) > 1 and split_name[1] in ['so', 'dll', 'pak', 'dylib', 'exe']:
                        look_for_source_map = False
                    
                    if look_for_source_map:

                        with input_zip_file.open(info.filename, 'r') as js_file:
                            result = sourcemap_pattern.search(js_file.read())
                            if result is not None:
                                source_map = result.group('sourceMap')
                    
                    symbol_check_output = None

                    entry = ClientManifestZipFileEntry(info.filename, info.compress_size, info.CRC, info.comment, source_map, symbol_check_output)
                    cdm_manifest_zip_file.contains.append(entry)


        except BadZipFile:
            #print(fpath)
            pass
        except:
            raise

    def cm_by_name(self, name):
        if name in self.map_cdnclientmanifest_name_to_obj:
            return self.map_cdnclientmanifest_name_to_obj[name]
        else:
            self.map_cdnclientmanifest_name_to_obj[name] = CDNClientManifest(name, None)
            return self.map_cdnclientmanifest_name_to_obj[name]

    def cmz_by_hash(self, hash, pretty_filename=None, ugly_name=None):
        if hash not in self.map_clientmanifestzipfile_hash_to_object:
            self.map_clientmanifestzipfile_hash_to_object[hash] = ClientManifestZipFile("global", hash, pretty_filename, ugly_name, None, None)
        return self.map_clientmanifestzipfile_hash_to_object[hash]


    def cm_objs(self):
        for x in sorted(self.map_cdnclientmanifest_name_to_obj.keys(), key=lambda y: self.map_cdnclientmanifest_name_to_obj[y].name):
            yield self.map_cdnclientmanifest_name_to_obj[x]

    def cmzf_objs(self):
        for x in sorted(self.map_clientmanifestzipfile_hash_to_object.keys(), key=lambda y: self.map_clientmanifestzipfile_hash_to_object[y].ugly_name):
            yield self.map_clientmanifestzipfile_hash_to_object[x]

    def cmzfe_objs(self, cmzfe):
        for x in sorted(cmzfe.contains, key=lambda x: x.filename):
            yield x
