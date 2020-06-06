
class Chunk:
    """
    The chunk class
    Will be basically used act as proxy to points between segments
    So we can have a chunk in the middle of a segment, to preserve virtual address space as I don't want to create new segments for every patch
    """
    def __init__(self, segment, start_offset, size):
        self._segment = segment
        self._start_offset = start_offset
        self._size = size
        self.flags = segment.flags

        self._virtual_address = segment.virtual_address + start_offset

    #@ property's just to stay up to date with new python features
    @property
    def size(self):
        return self._size

    @property
    def virtual_address(self):
        return self._virtual_address

    @property 
    def content(self):
        return self._segment.content

    @content.setter
    def content(self, new_content):
        self.update_data(content)

    def update_data(self, content):
        if len(content) > self._size:
            raise Exception("Content larger than size")
        self._segment.update_data(content, start_offset=self._start_offset)

