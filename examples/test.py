from ELFPatch import ELFPatch

f = ELFPatch(b"./test")

new_patch = f.new_patch(virtual_address=f.elf.ehdr.e_entry, size=0x100, append_original_instructions=True, append_jump_back=True)

new_patch.update_patch(f.assembler.assemble("""
push rax
push rdi
push rsi
push rdx
jmp get_str

make_syscall:
pop rsi

;call 0x1030 (relative address for puts)

mov rax, 0x1
mov rdi, 0x1
mov rdx, 12
syscall
jmp end

get_str:
call make_syscall
.string "SICED PATCH\\n"

end:
pop rdx
pop rsi
pop rdi
pop rax
""",offset=new_patch.chunk.virtual_address))


print("New Patch at", hex(new_patch.chunk.virtual_address))
f.write_file("./out")
