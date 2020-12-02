# ELFPatch

A library to manipulate and patch ELFs with dynamically sized patches.  

# Why

Mainly for CTFs and blackbox fuzzing. There have been times where I've wanted to patch ELFs but not enough space was available to do it inline, hence this was created. 

I've tried using multiple other ELF patching programs, but none of them fit my needs/worked on my usecases. 

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
    - One specific loader would only load a binary if the segments were in ascending order??!?!?

# Documentation

Sorry, there's no documentation available yet. You can read the API below or look at the examples directory.

# API

Credits to @LevitatingLion for this.

```python
class ELFPatch:

    def __init__(self, file_or_path):
        ...

    def new_chunk(self, size, prot='rwx', align=0x1) -> Chunk: #raw memory chunk for anything
        ...

    def new_patch(self, virtual_address, size=None, content=b"", append_jump_back=True, append_original_instructions=True) -> Patch:
        ...

    def write_file(self, filename): #writes patched ELF to file
        ...

class Patch:

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

class Chunk:

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


