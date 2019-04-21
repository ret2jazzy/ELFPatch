from .constants import *

class Segment:
    def __init__(self, physical_offset, virtual_address, size, flags=PT_R|PT_W|PT_X, align=0x10, content=b""):
        if len(content) > size:
            raise Exception("Content is larger than size")

        self.physical_offset = physical_offset
        self.virtual_address = virtual_address 
        self.flags = flags
        self.size = size
        self.align = align
        self.content = bytearray(content)
    
    def update_data(self, content, start_offset=None, end_offset=None):
        """
        Update content between start and end offset
        if None are provided, update from 0
        """
        if len(content) > self.size:
            raise Exception("Content is larger than size")

        if start_offset is None:
            start_offset = 0
        if end_offset is None:
            end_offset = start_offset+len(content)

        #Check if the end offset is greater than current content
        if end_offset > len(self.content):
            self.content += (end_offset - len(self.content)) * b"\x00"

        self.content[start_offset:end_offset] = content
  
