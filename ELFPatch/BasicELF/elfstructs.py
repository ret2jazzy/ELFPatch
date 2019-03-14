
class ELFStructs:
    def __init__(self, ehdr=None, phdr=None, elf_file=None):
        self.Elf_ehdr = ehdr
        self.Elf_phdr = phdr
        self.Elf_file = elf_file
