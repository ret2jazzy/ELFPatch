from .BasicELF import BasicELF
from .BasicELF.constants import *
from .chunk_manager import ChunkManager
from .patch import Patch
from .pwnasm import PwnAssembler, PwnDisassembler
from keystone import *
from capstone import *

class ELFPatch(BasicELF):

    def __init__(self, ELFFile):
        super().__init__(ELFFile)
        self._chunks = []
        self.patches = []

        #Super hacky, only supporting x86 or x64 for now
        #TODO: Make it modular and support more architectures
        if self._bits == 32:
            self.assembler = PwnAssembler(KS_ARCH_X86, KS_MODE_32)
            self.disassembler = PwnDisassembler(CS_ARCH_X86, CS_MODE_32)
        else:
            self.assembler = PwnAssembler(KS_ARCH_X86, KS_MODE_64)
            self.disassembler = PwnDisassembler(CS_ARCH_X86, CS_MODE_64)


    def new_chunk(self, size=None, content=b"", flags=PT_R|PT_W|PT_X):
        if size is None:
            size = len(content)

        for chunk in self._chunks:
            #Do a try catch because Chunk manager creates exceptions when sizes or flags don't match
            try:
                new_chunk = chunk.new_chunk(size=size, flags=flags, content=content)
                #If no exception, then succeded, return
                return new_chunk
            #errorn in adding chunk, pass
            except Exception as e:
                # print(e)
                pass

        #No chunks could satisfy the request

        page_aligned_size = (size & -0x1000) + 0x1000
        #Page aligned size so we can use it wisely for future chunks too and do not end up wasting virtual address space

        new_segment = self.new_segment(size=page_aligned_size, flags=flags)

        managed_chunk = ChunkManager(new_segment)
        self._chunks.append(managed_chunk)
        
        return managed_chunk.new_chunk(size=size, content=content, flags=flags) 

    def new_patch(self, virtual_address, size=None, content=b"", append_jump_back=True, append_original_instructions=True):
        if size is None:
            size = len(content)

        physical_offset = self.virtual_to_physical(virtual_address)

        chunk_for_patch = self.new_chunk(size+0x10) #Extra size cuz we might need to append a jump back

        jump_to_chunk = self.assembler.assemble("jmp {}".format(chunk_for_patch.virtual_address), offset=virtual_address)
        from binascii import hexlify
        print(f"new_patch: target=0x{virtual_address:x}, patch=0x{chunk_for_patch.virtual_address:x}, asm={hexlify(jump_to_chunk)}")

        size_of_jump = len(jump_to_chunk)

        overwritten_instructions = b""
        #Basically start disasemling from the address where we have to patch to the point where we can overwrite it with jmp instruction and not fuck adjacent instructions
        #cuz x86 is not fixed length
        #Then we will pad the jmp with NOPs to take exactly as much as a full disassembled instruction so that we don't have broken instructions
        for instr in self.disassembler.disassemble(self.rawelf[physical_offset:], offset=virtual_address):
            overwritten_instructions += instr.bytes
            #If we have disassembled enough
            if len(overwritten_instructions) >= size_of_jump:
                break
        #Pad it
        jump_to_chunk += b"\x90"*(len(overwritten_instructions) - size_of_jump) 

        new_patch = Patch(chunk_for_patch, virtual_address, patched_jump=jump_to_chunk, assembler=self.assembler, append_jump_back=append_jump_back, append_original_instructions=append_original_instructions, original_instructions=overwritten_instructions)

        self.patches.append(new_patch)
        return new_patch

    #Override the original _update_raw_elf to now add the patches in the rawelf

    def _update_raw_elf(self):
        #Call the original update to get the segments added
        super()._update_raw_elf()

        for patch in self.patches:
            physical_offset_patch = self.virtual_to_physical(patch.virtual_address)
            self.rawelf[physical_offset_patch:physical_offset_patch+len(patch.patched_jump)] = patch.patched_jump

