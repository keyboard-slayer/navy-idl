#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast
import re
from dataclasses import dataclass
from os.path import basename
from inspect import getsource, getfile, getmodule
from hashlib import md5
from types import ModuleType
from typing import TypeVar

u32 = TypeVar("u32")
i32 = TypeVar("i32")
size = TypeVar("size")
T = TypeVar("T")
struct = dataclass
interfaces = []
struct_defined = []
enums = {}


def auto():
    pass


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
        self.vtable = []
        self.endpoint_name = ""
        self.headers = set(["navy/ipcpack.h"])
        self.name = module_name.capitalize()
        self.endpoint = endpoint_name
        self.module = module
        self.source_code = [
            f"\n#define {module_name.upper()}_ID 0x{md5(module_name.encode()).hexdigest()[17:]}\n",
        ]

    def visit_FunctionDef(self, node):
        arg_lst = []

        self.endpoint_name = node.name.capitalize()
        struct_name = f"{self.name}{self.endpoint}{self.endpoint_name}Request"
        struct = "typedef struct \n{\n"
        for arg in node.args.args:
            arg_lst += f"{to_ctype(arg.annotation.id, self.headers, self.module, self.source_code)}"
            struct += f"    {to_ctype(arg.annotation.id, self.headers, self.module, self.source_code)} {arg.arg};\n"
        struct += f"}} {struct_name};\n"

        self.source_code.append(struct)
        self.source_code.append(
            f"void ipc_pack_{self.name.lower()}_{self.endpoint.lower()}_request(IpcPack *self, {struct_name} *data);"
        )
        self.source_code.append(
            f"void ipc_unpack_{self.name.lower()}_{self.endpoint.lower()}_request(IpcPack *self, {struct_name} *data);\n"
        )

        self.vtable.append(f"{self.name}{self.endpoint}{self.endpoint_name}")
        self.source_code.append(
            f"typedef void {self.vtable[-1]}(void *self, {struct_name} const *req, {to_ctype(node.returns.id, self.headers, self.module, self.source_code)} *resp);\n"
        )


def endpoint(self):
    methods = list(filter(lambda att: not att.startswith("__"), dir(self)))
    module_name = basename(getfile(self)).split(".")[0]
    for method in methods:
        func = getsource(getattr(self, method)).strip()
        compiler = CGen(
            self.__name__, module_name, getmodule(self)
        )
        compiler.visit(ast.parse(func))

        with open(f"{basename(getfile(self)).split('.')[0]}.h", "w") as f:
            f.write("#pragma once\n\n")
            for header in compiler.headers:
                f.write(f"#include <{header}>\n")

            f.write("\n".join(compiler.source_code))
            f.write("\ntypedef struct\n{\n")
            for vtable in compiler.vtable:
                f.write(f"    {vtable} *{re.sub(r'(?<!^)(?=[A-Z])', '_', vtable).lower()};\n")
            f.write(f"}} {self.__name__.capitalize()}{module_name.capitalize()}{compiler.endpoint_name}Vtable;\n")


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
