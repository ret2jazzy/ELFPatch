from construct import *

#32 bit ELF struct type definitions
Elf32_Addr = Int32ul
Elf32_Half = Int16ul
Elf32_Off = Int32ul
Elf32_Sword = Int32sl
Elf32_Word = Int32ul

#64 bit ELF struct definitions
Elf64_Addr = Int64ul
Elf64_Half = Int16ul
Elf64_SHalf = Int16sl
Elf64_Off = Int64ul
Elf64_Sword = Int32sl
Elf64_Word = Int32ul
Elf64_Xword = Int64ul
Elf64_Sxword = Int64sl
