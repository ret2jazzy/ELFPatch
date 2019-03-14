from construct import *
from .types import *

#32 bit header struct

Elf32_Ehdr = Struct(
        'e_ident' / Struct(
            "MAGIC"/Const(b"\x7fELF"), #ELF Header
            'EI_CLASS'/ Int8ul,
            "OTHER_STUFF"/ Array(11, Int8ul)
            ),
        'e_type' / Elf32_Half,
        'e_machine' / Elf32_Half,
        'e_version' / Elf32_Word,
        'e_entry' / Elf32_Addr,  
        'e_phoff' / Elf32_Off,
        'e_shoff' / Elf32_Off,
        'e_flags' / Elf32_Word,
        'e_ehsize' / Elf32_Half,
        'e_phentsize' / Elf32_Half,
        'e_phnum' / Elf32_Half,
        'e_shentsize' / Elf32_Half,
        'e_shnum' / Elf32_Half,
        'e_shstrndx' / Elf32_Half
        )
#32 bit Segment (program) header struct
Elf32_Phdr = Struct(
        'p_type' / Elf32_Word,
        'p_offset' / Elf32_Off,
        'p_vaddr' / Elf32_Addr,
        'p_paddr' / Elf32_Addr,
        'p_filesz' / Elf32_Word,
        'p_memsz' / Elf32_Word,
        'p_flags' / Elf32_Word,
        'p_align' / Elf32_Word
        )


Elf64_Ehdr = Struct(
        'e_ident' / Struct(
            "MAGIC"/Const(b"\x7fELF"), #ELF Header
            'EI_CLASS'/ Int8ul,
            "OTHER_STUFF"/ Array(11, Int8ul)
            ),
        'e_type' / Elf64_Half,
        'e_machine' / Elf64_Half,
        'e_version' / Elf64_Word,
        'e_entry' / Elf64_Addr,
        'e_phoff' / Elf64_Off,	
        'e_shoff' / Elf64_Off,	
        'e_flags' / Elf64_Word,
        'e_ehsize' / Elf64_Half,
        'e_phentsize' / Elf64_Half,
        'e_phnum' / Elf64_Half,
        'e_shentsize' / Elf64_Half,
        'e_shnum' / Elf64_Half,
        'e_shstrndx' / Elf64_Half
        )


Elf64_Phdr = Struct(
        'p_type' / Elf64_Word,
        'p_flags' / Elf64_Word,
        'p_offset' / Elf64_Off,
        'p_vaddr' / Elf64_Addr,
        'p_paddr' / Elf64_Addr,
        'p_filesz' / Elf64_Xword,
        'p_memsz' / Elf64_Xword,
        'p_align' / Elf64_Xword
        )

Elf32_file = Struct(
        'ehdr' / Elf32_Ehdr,
        Padding(this.ehdr.e_phoff - Elf32_Ehdr.sizeof()),
        'phdr_table' / Array(this.ehdr.e_phnum, Elf32_Phdr)
        )

Elf64_file = Struct(
        'ehdr' / Elf64_Ehdr, 
        Padding(this.ehdr.e_phoff - Elf64_Ehdr.sizeof()),
        'phdr_table' / Array(this.ehdr.e_phnum, Elf64_Phdr)
        )   
