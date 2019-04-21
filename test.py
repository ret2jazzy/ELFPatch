from ELFPatch import ELFPatch 
from ELFPatch.BasicELF import constants

f = ELFPatch(b"./test")

print("Adding new chunks")

new_chunk = f.new_chunk(size=0x20)
new_chunk_2 = f.new_chunk(size=0x20, flags=constants.PT_R)
new_chunk_3 = f.new_chunk(size=0x20)

new_chunk.update_content(b"AAAA")
new_chunk_2.update_content(b"BBBB")
new_chunk_2.update_content(b"CCCC")

print("New chunk at", hex(new_chunk.virtual_address))
print("New chunk at", hex(new_chunk_2.virtual_address))
print("New chunk at", hex(new_chunk_3.virtual_address))

f.write_file("./out")
