from ELFPatch.BasicELF import BasicELF

f = BasicELF(b"./test")
f._update_raw_elf()
f.add_segment()
f.write_file("./outp")
