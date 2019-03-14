from .elfstructs import *
from . import structs as StructSkeletons 
from .constants import *
from construct import *
from .segment import *

class BasicELF:
    def __init__(self, ELFFile):
        with open(ELFFile, "rb") as f:
            self.rawelf = bytearray(f.read())

        self._init_structs()

        self.elf = self._structs.Elf_file.parse(self.rawelf)

        self.new_segments = []
        self.phdr_fixed = False

    def write_file(self, filename):
        self._update_raw_elf()
        with open(filename, "wb") as f:
            f.write(self.rawelf)

    def add_segment(self, content=b"", flags=PT_R|PT_W|PT_X, type=PT_LOAD, size=0x100, align=0x1000):
        if not self.phdr_fixed:
            self.phdr_fixed = True
            offset, virt_addr = self.add_segment(size=0x500, flags=PT_R|PT_W|PT_X)
            self._fix_pdhr_entry(offset, virt_addr)
            return

        raw_offset = self._find_usable_physical_offset()
        virtual_addr = self._get_next_non_conflicting_virtual_address()

        #Create a raw segment struct using the Container from construct
        segment_struct = Container(p_type=type, p_flags=flags, p_offset=raw_offset, p_vaddr=virtual_addr,p_paddr=virtual_addr, p_filesz=size, p_memsz=size, p_align=align)

        self.elf.phdr_table.append(segment_struct)
        self.elf.ehdr.e_phnum += 1

        #Create a new segment class, but this time for segment addition
        segment_to_add = Segment(raw_offset, virtual_addr, size, flags=flags, align=align, content=content)
        self.new_segments.append(segment_to_add)

        return raw_offset, virtual_addr 

    #Basically move the phdr to the bottom to make more space
    def _fix_pdhr_entry(self, offset, virt_addr):
        self.elf.ehdr.e_phoff = offset

        for entry in self.elf.phdr_table:
            if entry.p_type == PT_PHDR:
                #Set the binary offset
                entry.p_offset = self.elf.ehdr.e_phoff
                #Set the virtual addresses 
                entry.p_vaddr = virt_addr 
                entry.p_paddr = virt_addr 
                #Set the size to a large-ish number
                entry.p_memsz = 0x500
                entry.p_filesz = 0x500

                break

    def _find_usable_physical_offset(self):
        if len(self.new_segments) == 0:
            return (len(self.rawelf) & -0x1000) + 0x1000

        return (self.new_segments[-1].offset & -0x1000) + 0x1000

    def _get_next_non_conflicting_virtual_address(self, permissions=PT_R|PT_W|PT_X):
        current_max = 0x0
        PAGE_SIZE = 0x1000

        max_addr = max(self.elf.phdr_table, key=(lambda entry: entry.p_vaddr + entry.p_memsz)) 

        if max_addr.p_flags == permissions:
            return max_addr.p_vaddr + max_addr.p_memsz + 0x10

        return (((((max_addr.p_vaddr + max_addr.p_memsz) & -max_addr.p_align) + max_addr.p_align) & -PAGE_SIZE) + PAGE_SIZE)

    def _init_structs(self):
        if self.rawelf[4] == 0x1: #4th byte identifies the ELF type
            self._bits = 32
        elif self.rawelf[4] == 0x2:
            self._bits = 64
        else:
            raise Exception("Not a valid 32/64 bit ELF")

        self._structs = ELFStructs()
            #Initialize the structures used based on the bitsize so we don't have to look them up everytime
        if self._bits == 32:
            self._structs.Elf_file = StructSkeletons.Elf32_file
            self._structs.Elf_ehdr = StructSkeletons.Elf32_Ehdr 
            self._structs.Elf_phdr = StructSkeletons.Elf32_Phdr 
        else:
            self._structs.Elf_file = StructSkeletons.Elf64_file
            self._structs.Elf_ehdr = StructSkeletons.Elf64_Ehdr 
            self._structs.Elf_phdr = StructSkeletons.Elf64_Phdr 

    def _update_raw_elf(self):
        # write the ELF header
        self.rawelf[0:self._structs.Elf_ehdr.sizeof()] = self._structs.Elf_ehdr.build(self.elf.ehdr) 

        #add the new updated LOAD segment's data in the ELF
        for segment in self.new_segments:
            segment_end = (segment.offset + segment.size)
            if segment_end > len(self.rawelf):
                self.rawelf += b"\x00" * (segment_end - len(self.rawelf) + 1)
                self.rawelf[segment.offset:segment.offset+len(segment.content)] = segment.content

        self.new_segments = []

        #get location of Phdr table (segement table) and size
        phdr_offset = self.elf.ehdr.e_phoff 
        phdr_size = self.elf.ehdr.e_phnum * self.elf.ehdr.e_phentsize
        phdr_end = phdr_offset + phdr_size

        #Check if Phdr table is after the end of the binary, and pad it with nulls if it is
        if phdr_end > len(self.rawelf):
            self.rawelf += b"\x00" * (phdr_end - len(self.rawelf)) 

        #Due to the limitations of the construct library (Not dynamic arrays), I create a new phdr_table struct to finally serialize the phdr in raw bytes
        self.rawelf[phdr_offset:phdr_end] = Array(self.elf.ehdr.e_phnum, self._structs.Elf_phdr).build(self.elf.phdr_table)



