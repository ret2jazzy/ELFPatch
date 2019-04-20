from .constants import *

class Segment:
    def __init__(self, physical_offset, addr, size, flags=PT_R|PT_W|PT_X, align=0x10, content=b""):
        if len(content) > size:
            raise Exception("Content is larger than size")
        self.physical_offset = physical_offset
        self.virtual_address = addr
        self.flags = flags
        self.size = size
        self.align = align
        self.content = content

    def update_content(self, content):
        if len(content) > self.size:
            raise Exception("Content is larger than size")
        self.content = content

    def add_content(self, content):
        if len(content + self.content) > self.size:
            raise Exception("Content is larger than size")
        self.content += content


