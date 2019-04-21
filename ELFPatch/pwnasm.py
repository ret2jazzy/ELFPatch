from keystone import *
from capstone import *

class PwnAssembler:
    def __init__(self, arch, mode):
        self.arch = arch
        self.mode = mode

        self.assembler = Ks(arch, mode)

    def assemble(self, data, offset=0):
        return bytes(self.assembler.asm(data, offset)[0])

class PwnDisassembler:
    def __init__(self, arch, mode):
        self.arch = arch
        self.mode = mode

        self.disassembler = Cs(arch, mode)

    def disassemble(self, data, offset=0x0):
        return self.disassembler.disasm(data, offset)

