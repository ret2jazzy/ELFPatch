from ..BasicELF import BasicELF
from ..BasicELF.constants import PT_LOAD, PT_R, PT_W
from .platform_specifics import platforms

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

from io import BytesIO


def hook_elf(target, hooks):
    """Install all hooks into the target.

    target: BasicELF
    hooks: ELFFile (from pyelftools)
    """

    def embed_elf():
        # add segments from hooks binary
        for segment in hooks.iter_segments():
            if segment.header.p_type != 'PT_LOAD':
                continue

            segment = target.new_segment(
                content=segment.data(),
                flags=segment.header.p_flags,
                size=segment.header.p_memsz,
                align=segment.header.p_align,
                virtual_address=virt_base + segment.header.p_vaddr)
            print(
                f"Added segment at vaddr 0x{segment.virtual_address:x}, offset 0x{segment.physical_offset:x}")

    def hook_entry():
        from binascii import hexlify

        print("Hooking entry point")
        data = target.new_chunk(0x10, flags=PT_R | PT_W)
        print(f"data @ 0x{data.virtual_address:x}")

        patch_begin = target.new_patch(target.elf.ehdr.e_entry,
                                       len(gen_code_entry_begin(0x31337, 0, 0x31337)))
        patch_begin.append_original_instruction = False
        patch_begin.append_jump_back = False
        content = gen_code_entry_begin(data.virtual_address - patch_begin.chunk.virtual_address,
                                       virt_base + hooks.header['e_entry'] -
                                       patch_begin.chunk.virtual_address,
                                       fs_base.virtual_address - patch_begin.chunk.virtual_address)
        patch_begin.update_patch(content)
        print(f"patch_begin @ 0x{patch_begin.chunk.virtual_address:x}, content={hexlify(content)}")

        patch_end = target.new_patch(
            virt_base + hooks_symbols['_main_end'],
            len(gen_code_entry_end(0x31337, 0, 0x31337, patch_begin.original_instructions)))
        patch_end.append_original_instruction = False
        patch_end.append_jump_back = False
        content = gen_code_entry_end(
            data.virtual_address - patch_end.chunk.virtual_address,
            target.elf.ehdr.e_entry + len(patch_begin.original_instructions) -
            patch_end.chunk.virtual_address,
            fs_base.virtual_address - patch_end.chunk.virtual_address,
            patch_begin.original_instructions)
        patch_end.update_patch(content)
        print(f"patch_end @ 0x{patch_end.chunk.virtual_address:x}, content={hexlify(content)}")

    def hook_user_functions():
        print("hooking user functions")
        for section in hooks.iter_sections():
            if not isinstance(section, SymbolTableSection):
                continue
            for symbol in section.iter_symbols():
                if not symbol.name.startswith('hook_'):
                    continue

                address = symbol.name[5:]
                try:
                    address = int(address, 16)
                except ValueError:
                    pass

                hook_function(address, symbol.entry.st_value)

    def hook_function(address, hook):
        from binascii import hexlify

        # resolve address
        if isinstance(address, str):
            address = target_symbols[address]
        # adjust hook to virtual address
        hook += virt_base

        print(f"Hooking addr 0x{address:x} with hook 0x{hook:x}")

        patch = target.new_patch(address, len(gen_code_hook(0, 0x31337)))
        patch.append_original_instruction = True
        patch.append_jump_back = True
        content = gen_code_hook(hook - patch.chunk.virtual_address,
                                fs_base.virtual_address - patch.chunk.virtual_address)
        patch.update_patch(content)
        print(f"patch @ 0x{patch.chunk.virtual_address:x}, content={hexlify(content)}")

    def gen_code_hook(call_offset, fs_base_offset):
        code = b''
        code += platform.save_registers()
        code += platform.swap_fs_base(fs_base_offset - len(code))
        code += platform.relative_call(call_offset - len(code))
        code += platform.swap_fs_base(fs_base_offset - len(code))
        code += platform.restore_registers()
        return code

    def gen_code_entry_begin(data_offset, jump_offset, fs_base_offset):
        code = b''
        code += platform.save_registers()
        code += platform.save_stackpointer(data_offset - len(code))
        code += platform.swap_fs_base(fs_base_offset - len(code))
        code += platform.fake_initial_stack()
        code += platform.zero_registers()
        code += platform.relative_jump(jump_offset - len(code))
        return code

    def gen_code_entry_end(data_offset, jump_offset, fs_base_offset, original_instructions):
        code = b''
        code += platform.swap_fs_base(fs_base_offset - len(code))
        code += platform.restore_stackpointer(data_offset - len(code))
        code += platform.restore_registers()
        code += original_instructions
        code += platform.relative_jump(jump_offset - len(code))
        return code

    def elf_symbols(elf):
        symbols = {}
        for section in elf.iter_sections():
            if not isinstance(section, SymbolTableSection):
                continue
            for symbol in section.iter_symbols():
                symbols[symbol.name] = symbol.entry.st_value
        return symbols

    def smallest_free_address():
        addr = max(s.p_vaddr + s.p_memsz for s in target.elf.phdr_table if s.p_type == PT_LOAD)
        addr = (addr + 0x3000) & ~0xfff
        addr = (addr + 0x100000) & ~0xfffff
        return addr

    # get platform specifics
    platform = platforms[target.elf.ehdr.e_machine](target.assembler)
    print("platform:", platform)

    # get symbols
    target_symbols = elf_symbols(ELFFile(BytesIO(target.rawelf)))
    hooks_symbols = elf_symbols(hooks)

    # get smallest free virtual address
    virt_base = smallest_free_address()
    print("virt_base:", hex(virt_base))

    embed_elf()

    fs_base = target.new_chunk(0x10, flags=PT_R | PT_W)
    print(f"fs_base @ 0x{fs_base.virtual_address:x}")

    hook_entry()
    hook_user_functions()

    segment = target.new_segment(
        content=b'',
        flags=PT_R | PT_W,
        size=0x10,
        align=0x1000,
        virtual_address=smallest_free_address() + 0x1000)
    print(
        f"Added segment at vaddr 0x{segment.virtual_address:x}, offset 0x{segment.physical_offset:x}")
