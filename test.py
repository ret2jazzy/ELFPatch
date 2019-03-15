from ELFPatch.BasicELF import BasicELF

f = BasicELF(b"./test")

print("Adding new segment")

f.add_segment(content=b"BBBB")

print("New segment added at 0x{:x}".format(f.new_segments[0].address))

f.write_file("./out")
