from ELFPatch.BasicELF.basicelf import BasicELF

f = BasicELF(b"./test")
print(f.ELFHeader)


