# PatchElf Library

## API

### patchelf.BasicElf

```python
class BasicElf:

    def __init__(self, file_or_path):
        ...

    @property
    def raw_elf(self) -> bytes:
        ...

    def new_segment(self, size, flags=PT_R | PT_W | PT_X, type=PT_LOAD, align=0x1000, virtual_address=None) -> Segment:
        ...


class Segment:

    @property
    def virtual_address(self) -> int:
        ...

    @property
    def file_offset(self) -> int:
        ...

    @property
    def size(self) -> int:
        ...

    @property
    def flags(self) -> int:
        ...

    @property
    def align(self) -> int:
        ...

    @property
    def content(self) -> bytes:
        ...

    @content.setter
    def content(self, new_content):
        ...
```

### patchelf.ChunkElf

```python
class ChunkElf(BasicElf):

    def __init__(self, file_or_path):
        ...

    def new_chunk(self, size, flags=PT_R | PT_W | PT_X) -> Chunk:
        ...


class Chunk:

    @property
    def segment(self) -> Segment:
        ...

    @property
    def virtual_address(self) -> int:
        ...

    @property
    def file_offset(self) -> int:
        ...

    @property
    def segment_offset(self) -> int:
        ...

    @property
    def size(self) -> int:
        ...

    @property
    def flags(self) -> int:
        ...

    @property
    def content(self) -> bytes:
        ...

    @content.setter
    def content(self, new_content):
        ...
```

### patchelf.PatchElf

```python
class PatchElf(ChunkElf):

    def __init__(self, file_or_path):
        ...

    def new_patch(self, patchee, size) -> Patch:
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

### BasicElf

- Segments stored in internal list

- Packed when creating raw elf

### ChunkElf

- `ChunkAllocator`: Manage and allocate chunks

- `ChunkedSegment`: Segment consisting only of chunks, packed to concatenation of its chunks, stores a list of its chunks

### PatchElf

- `PatchChunk`: Packed to patch with optionally appended original instruction and jump back
