from navy import *

@enum 
class VfsFlags:
    DIR = auto()
    FILE = auto()
    CHAR = auto()
    BLOCK = auto()
    PIPE = auto()
    SYMLINK = auto()
    MOUNTPOINT = auto()


@struct 
class VfsNode:
    name: str 
    size: size


@endpoint
class Inode:
    def open(path: str) -> VfsNode: pass