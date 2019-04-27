#!/usr/bin/env python3

import sys
from os import system
from time import sleep

from elftools.elf.elffile import ELFFile

from ELFPatch.elfhook import hook_elf
from ELFPatch.elfpatch import ELFPatch


def main(args):
    if len(args) != 3:
        print("Usage: elfhook.py <target> <hooks>")
        exit()
    target_path = args[1]
    hooks_path = args[2]

    target = ELFPatch(target_path)
    hooks = ELFFile(open(hooks_path, 'rb'))

    hook_elf(target, hooks)

    target.write_file(target_path + '.patched')
    sleep(0.1)
    system(f'chmod +x "{target_path}".patched')
    sleep(0.1)


if __name__ == "__main__":
    main(sys.argv)
