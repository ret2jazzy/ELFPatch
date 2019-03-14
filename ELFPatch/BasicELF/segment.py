from .constants import *

class Segment:
    def __init__(self, offset, addr, size, flags=PT_R|PT_W|PT_X, align=0x10, content=b""):
        self.offset = offset
        self.address = addr
        self.flags = flags
        self.size = size
        self.align = align
        self.content = content

