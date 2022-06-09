#pragma once

#include <brutal/str.h>
#include <navy/ipcpack.h>
#include <stddef.h>

#define VFS_ID 0x1fcdbae6fdd4465

typedef struct 
{
    Str path;
} VfsInodeOpenRequest;

void ipc_pack_vfs_inode_request(IpcPack *self, VfsInodeOpenRequest *data);
void ipc_unpack_vfs_inode_request(IpcPack *self, VfsInodeOpenRequest *data);

typedef struct
{
    Str name;
    size_t size;
} VfsNode;

typedef void VfsInodeOpen(void *self, VfsInodeOpenRequest const *req, VfsNode *resp);

typedef struct
{
    VfsInodeOpen *vfs_inode_open;
} InodeVfsOpenVtable;
