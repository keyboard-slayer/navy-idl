from navy import *


@enum
class FsFlags:
    DIR = auto()
    FILE = auto()
    CHAR = auto()
    BLOCK = auto()
    PIPE = auto()
    SYMLINK = auto()
    MOUNTPOINT = auto()


@struct
class FsNode:
    name: str
    flags: FsFlags
    perm: u32
    size: size


@endpoint
class Vfs:
    # def resolve_path(path: str) -> FsNode: pass
    def test(node: FsNode) -> str:
        pass
