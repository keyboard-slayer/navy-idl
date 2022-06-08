#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast
from inspect import getsource
from ctypes import (
    c_int32,
    c_uint32,
)
from uuid import uuid4

u32 = c_uint32
i32 = c_int32


def to_ctype(name: str, header: set):
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

    return typename


class CGen(ast.NodeTransformer):
    def __init__(self, module_name: str):
        self.headers = set()
        self.source_code = [f"#define {module_name}_UUID 0x{uuid4().hex}"]
        print(self.source_code)

    def visit_FunctionDef(self, node):
        print(to_ctype(node.returns.id, self.headers))
        print(ast.dump(node))
        return "hi"


def endpoint(self):
    methods = list(filter(lambda att: not att.startswith("__"), dir(self)))
    funcs = []

    for method in methods:
        func = getsource(getattr(self, method)).strip()
        # print(ast.dump(ast.parse(func), indent=4))
        compiler = CGen(self.__name__)
        compiler.visit(ast.parse(func))
