from ELFPatch.BasicELF import BasicELF

f = BasicELF(b"./test")

print("Adding new segment")

f.add_segment(content=b"BBBB", virtual_address=0x808560)

print("New segment added at 0x{:x}".format(f.new_segments[0].virtual_address))

f.write_file("./out")
