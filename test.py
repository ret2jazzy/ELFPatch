from ELFPatch.BasicELF import BasicELF

f = BasicELF(b"./test")

print("Adding new segment")

new_segment = f.add_segment(size=0x2000)

print("New segment at", hex(new_segment.virtual_address))

new_segment.content = b"C"*0x100

f.write_file("./out")
