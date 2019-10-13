# PatchElf Library

## API

```python
class PatchElf:

    def __init__(self, file_or_path):
        ...

    @property
    def raw_elf(self) -> bytes:
        ...

    @property
    def lief(self) -> lief.ELF.Binary:
        ...

    def new_chunk(self, size, prot='rwx', align=0x1) -> Chunk:
        ...

    def new_patch(self, patchee, size) -> Patch:
        ...


class Chunk:

    @property
    def virtual_address(self) -> int:
        ...

    @property
    def file_offset(self) -> int:
        ...

    @property
    def prot(self) -> str:
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


class Patch:

    @property
    def chunk(self) -> Chunk:
        ...

    @property
    def patchee(self) -> int:
        ...

    @property
    def inserted_jump(self) -> bytes:
        ...

    @property
    def original_instructions(self) -> bytes:
        ...

    @property
    def append_jump_back(self) -> bool:
        ...

    @append_jump_back.setter
    def append_jump_back(self, append_jump):
        ...

    @property
    def append_original_instructions(self) -> bool:
        ...

    @append_original_instructions.setter
    def append_original_instructions(self, append_orig):
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

## Implementation Notes

- Two choices:

  - [ ] Lower layers propagate changes to higher layers in setters

  - [x] Higher layers get the lower layers' status when packing

### Chunk

- `ChunkAllocator`: Manage and allocate chunks

- `ChunkedSegment`: Segment consisting only of chunks, packed to concatenation of its chunks, stores a list of its chunks

### Patch

- `PatchChunk`: Packed to patch with optionally appended original instruction and jump back
