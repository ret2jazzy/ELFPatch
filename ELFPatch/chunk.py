
class Chunk:
    """
    The chunk class
    Will be basically used act as proxy to points between segments
    So we can have a chunk in the middle of a segment, to preserve virtual address space as I don't want to create new segments for every patch
    """
    def __init__(self, segment, start_offset, size):
        self._segment = segment
        self._start_offset = start_offset
        self.size = size
        self.flags = segment.flags

        self.virtual_address = segment.virtual_address + start_offset

    def update_data(self, content):
        if len(content) > self.size:
            raise Exception("Content larger than size")
        self._segment.update_data(content, start_offset=self._start_offset)

