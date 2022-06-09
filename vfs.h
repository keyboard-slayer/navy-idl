#pragma once

#include <stddef.h>
#include <brutal/str.h>
#include <navy/ipcpack.h>

#define VFS_ID 0x1fcdbae6fdd4465

typedef struct 
{
    Str path;
} VfsInodeOpenRequest;

void ipc_pack_vfs_inode_request(IpcPack *self, VfsInodeOpenRequest *data);
void ipc_unpack_vfs_inode_request(IpcPack *self, VfsInodeOpenRequest *data);

enum vfsflags
{
    VFSFLAGS_BLOCK,
    VFSFLAGS_CHAR,
    VFSFLAGS_DIR,
    VFSFLAGS_FILE,
    VFSFLAGS_MOUNTPOINT,
    VFSFLAGS_PIPE,
    VFSFLAGS_SYMLINK,
};

typedef struct
{
    Str name;
    size_t size;
    enum vfsflags type;
} VfsNode;

typedef void VfsInodeOpen(void *self, VfsInodeOpenRequest const *req, VfsNode *resp);

typedef struct
{
    VfsInodeOpen *vfs_inode_open;
} InodeVfsOpenVtable;
