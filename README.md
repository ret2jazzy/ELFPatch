# ELFPatch

A library to manipulate and patch ELFs with dynamically sized patches.  

# Why

Mainly for CTFs and blackbox fuzzing. There have been times where I've wanted to patch ELFs but not enough space was available to do it inline, which is why this was created. 

I've tried using few other ELF patching programs, but none of them fit my needs/worked on my usecases. 

# How 

The process of adding a patch briefly boils down to the following:

- New segments are added that hold a patch.
    - To add new segments, the segment table is first moved to the end of the binary. 
- The code at the patch address is replaced with a jump to the newly added segment.
- At the end of the patch, it jumps back to the original address.

### Issues faced

- Moving the segment table to the end was a huge hassle because of the diversity in ELF loaders.
    - Some binaries loaded with ld.so but broke with kernel's loader and vice versa. 
    - It turns out some worked with overlapping segments which others absolutely hated it. 
    - One specific loader would only load a binary if the segment's base addresses were in ascending order??!?!?

# Support

Currently only supports x86/64, but it shouldn't be hard to extend it to other architectures (only need to modify the assembler directives). I'll add other architectures when I get time.

# Bugs/issues

It's still in beta, so any issues and bugs are welcome.

# Documentation

Sorry, there's no documentation available yet. You can read the API below or look at the examples directory. For a little more complicated example, look at the debugging section of this [blogpost](http://blog.perfect.blue/Hack-A-Sat-CTF-2020-Launch-Link).

# API

Credits to @LevitatingLion for this.

```python
class ELFPatch: # The main patcher

    def __init__(self, file_or_path):
        ...

    def new_chunk(self, size, prot='rwx', align=0x1) -> Chunk:
        ...

    def new_patch(self, virtual_address, size=None, content=b"", append_jump_back=True, append_original_instructions=True) -> Patch:
        ...

    def write_file(self, filename): #writes patched ELF to file
        ...

class Patch: # The actual patch object

    @property
    def chunk(self) -> Chunk:
        ...

    @property
    def size(self) -> int:
        ...

    @property
    def content(self) -> bytes:
        ...

    @content.setter
    def content(self, new_content):
        ...

class Chunk: #raw memory chunk for anything

    @property
    def virtual_address(self) -> int:
        ...

    @property
    def size(self) -> int:
        ...

    @property
    def content(self) -> bytes:
        ...

    @content.setter
    def content(self, new_content):
        ...

```
