from typing import List, Set, Callable

from dataclasses import dataclass

@dataclass
class CDNClientManifest:
    name: str
    children: List['ClientManifestZipFile']
    def __post_init__(self):
        self.children = list()
        
@dataclass
class ClientManifestZipFileEntry:
    filename: str
    compress_size: str
    crc: str
    comment: str
    source_map: str  | None
    symbol_check_output: str | None

@dataclass
class ClientManifestZipFile:
    realm: str
    hash: str
    pretty_name: str | None
    ugly_name: str | None
    contains: List[ClientManifestZipFileEntry] | None
    parents: List[CDNClientManifest] | None

    def __post_init__(self):
        self.contains = list()
        self.parents = list()
        if self.pretty_name is None:
            self.pretty_name = ""
        if self.ugly_name is None:
            self.ugly_name = ""

@dataclass
class ResultFilter:
    output_filepath: str
    mzf_obj_condition: Callable[[ClientManifestZipFile], bool]
    cmzfe_obj_condition: Callable[[ClientManifestZipFileEntry], bool]
