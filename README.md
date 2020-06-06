# ELFPatch

A library to manipulate and patch ELFs.  

## API

Thanks to @LevitatingLion for writing this.

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





