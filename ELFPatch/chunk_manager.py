from .chunk import Chunk

class ChunkManager:
    """
    The class used to manage a Segment and dispatch chunks of appropriate size
    """
    def __init__(self, segment):
        self.managed_segment = segment
        self.max_size = segment.size
        self.used_size = len(segment.content)
        self.left_size = self.max_size - self.used_size

    def new_chunk(self, size=None,flags=None, content=b""):
        if size is None:
            size = len(content)

        if size > self.left_size:
            raise Exception("Size unavailable")

        if flags is None:
            flags = self.managed_segment.flags

        if flags != self.managed_segment.flags:
            raise Exception("Flags mismatch")

        new_chunk = Chunk(self.managed_segment, start_offset=self.used_size, size=size) 

        self.used_size += size
        self.left_size -= size

        return new_chunk

