import ELFPatch.BasicELF.structs as ELFStructure

class BasicELF:
    def __init__(self, ELFFile):
        with open(ELFFile, "rb") as f:
            self.rawelf = bytearray(f.read())
        
        self._init_structs()

        self.ELFHeader = self._ehdr.parse(self.rawelf)
    
    def _init_structs(self):
        if self.rawelf[4] == 0x1: #4th byte identifies the ELF type
            self._bits = 32
        elif self.rawelf[4] == 0x2:
            self._bits = 64
        else:
            raise Exception("Not a valid 32/64 bit ELF")

        if self._bits == 32:
            self._ehdr = ELFStructure.Elf32_Ehdr
            self._phdr = ELFStructure.Elf32_Phdr
        else:
            self._ehdr = ELFStructure.Elf64_Ehdr
            self._phdr = ELFStructure.Elf64_Phdr
