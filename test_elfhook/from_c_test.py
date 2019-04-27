#!/usr/bin/env python3

from ELFPatch.BasicELF import BasicELF
from ELFPatch.BasicELF.constants import PT_LOAD
from ELFPatch.hookelf import hook_elf

from elftools.elf.elffile import ELFFile

from os import system
from os.path import join
from tempfile import TemporaryDirectory

target_source = '''
#include <stdio.h>
#include <unistd.h>

void print(void) {
    puts("test");
    sleep(1);
}

int main(void) {
    while (1)
        print();
    return 0;
}
'''

hooks_source = '''
#include "ELFPatch/hookelf.h"
#include <stdio.h>

HOOK(print) {
    puts("print called");
}
'''


def main(tmp):
    print(f"Using temp dir {tmp}")

    target_path = compile(tmp, 'target', target_source)
    hooks_path = compile(tmp, 'hooks', hooks_source, static_pie=True)

    target = BasicELF(target_path)
    hooks = ELFFile(open(hooks_path, 'rb'))

    hook_elf(target, hooks)
    target.write_file(target_path + '.patched')
    input("> ")


def compile(tmp, name, source, static_pie=False):
    path_src = join(tmp, name + '.c')
    path_bin = join(tmp, name)

    with open(path_src, 'w') as f:
        f.write(source)

    args = ' -Wall -Wextra -O3 -I.'
    if static_pie:
        args += ' -static-pie'
    system(f'gcc-8{args} {path_src} -o {path_bin}')

    return path_bin


if __name__ == "__main__":
    with TemporaryDirectory() as tmp:
        main(tmp)
