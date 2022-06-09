#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast
from dataclasses import dataclass
from os.path import basename
from inspect import getsource, cleandoc, getfile, getmodule
from hashlib import md5
from types import ModuleType
from typing import TypeVar, Annotated

u32 = TypeVar("u32")
i32 = TypeVar("i32")
size = TypeVar("size")
T = TypeVar("T")
struct = dataclass
struct_defined = []
enums = {}


def auto():
    pass


class Ptr:
    def __init__(self, container):
        self.container = container
        self.__name__ = "Ptr"

def to_ctype(name: str, header: set, module: ModuleType, code: list):
    typename = ""
    match name:
        case "i32":
            typename = "int32_t"
            header.add("stdint.h")
        case "u32":
            typename = "uint32_t"
            header.add("stdint.h")
        case "str":
            typename = "Str"
            header.add("brutal/str.h")
        case "size":
            typename = "size_t"
            header.add("stddef.h")
        case _:
            source = ""
            typename = name

            if not hasattr(module, name):
                raise NameError(f"name '{name}' is not defined")

            elif (
                hasattr(getattr(module, name), "__dataclass_fields__")
                and name not in struct_defined
            ):
                fields = getattr(getattr(module, name), "__dataclass_fields__")
                source += "typedef struct\n{\n"
                for field in fields.values():
                    source += f"    {to_ctype(field.type.__name__, header, module, code)} {field.name};\n"
                source += f"}} {name};\n"

                code.append(source)

            elif name in enums.keys():
                typename = f"enum {typename.lower()}"
                code.append(enums[name])
            
            else:
                raise NameError(f"name '{name}' is not defined")

    return typename


class CGen(ast.NodeTransformer):
    def __init__(self, endpoint_name: str, module_name: str, module: ModuleType):
        self.headers = set(["navy/ipcpack.h"])
        self.name = module_name.capitalize()
        self.endpoint = endpoint_name
        self.module = module
        self.source_code = [
            f"#define {module_name.upper()}_ID 0x{md5(module_name.encode()).hexdigest()[17:]}\n",
        ]

    def visit_FunctionDef(self, node):
        struct_name = f"{self.name}{self.endpoint}{node.name.capitalize()}Request"
        struct = "typedef struct \n{\n"
        for arg in node.args.args:
            struct += f"    {to_ctype(arg.annotation.id, self.headers, self.module, self.source_code)} {arg.arg};\n"
        struct += f"}} {struct_name};\n"

        self.source_code.append(struct)
        self.source_code.append(
            f"void ipc_pack_{self.name.lower()}_{self.endpoint.lower()}_request(IpcPack *self, {struct_name} *data);"
        )
        self.source_code.append(
            f"void ipc_unpack_{self.name.lower()}_{self.endpoint.lower()}_request(IpcPack *self, {struct_name} *data);"
        )


def endpoint(self):
    methods = list(filter(lambda att: not att.startswith("__"), dir(self)))
    funcs = []

    for method in methods:
        func = getsource(getattr(self, method)).strip()
        compiler = CGen(
            self.__name__, basename(getfile(self)).split(".")[0], getmodule(self)
        )
        compiler.visit(ast.parse(func))

        print("#pragma once\n")
        for header in compiler.headers:
            print(f"#include <{header}>")
        print("")
        print("\n".join(compiler.source_code))


def enum(self):
    fields = list(filter(lambda att: not att.startswith("__"), dir(self)))
    source_code = f"enum {self.__name__.lower()}\n{{\n"
    for field in fields:
        if getattr(self, field) == None:
            source_code += f"    {self.__name__.upper()}_{field.upper()},\n"
        else:
            source_code += f"    {self.__name__.upper()}_{field.upper()} = {getattr(self, field).__repr__()},\n"
    source_code += "};\n"
    enums[self.__name__] = source_code
    return self
