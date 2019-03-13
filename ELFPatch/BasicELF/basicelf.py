from .elfstructs import *
from . import structs as StructSkeletons 

class BasicELF:
    def __init__(self, ELFFile):
        with open(ELFFile, "rb") as f:
            self.rawelf = bytearray(f.read())
        
        self._init_structs()

        self.elf = self._structs.elf_file.parse(self.rawelf)


    def _init_structs(self):
        if self.rawelf[4] == 0x1: #4th byte identifies the ELF type
            self._bits = 32
        elif self.rawelf[4] == 0x2:
            self._bits = 64
        else:
            raise Exception("Not a valid 32/64 bit ELF")

        self._structs = ELFStructs()

        if self._bits == 32:
            self._structs.elf_file = StructSkeletons.Elf32_file
        else:
            self._structs.elf_file = StructSkeletons.Elf64_file
