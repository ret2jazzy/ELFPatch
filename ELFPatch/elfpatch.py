from .BasicELF import BasicELF
from .BasicELF.constants import *
from .chunk_manager import ChunkManager

class ELFPatch(BasicELF):

    def __init__(self, ELFFile):
        super().__init__(ELFFile)
        self._chunks = []

#     def add_patch(self, virtual_address, size=None,content=b""):
        # if size is None:
            # size = len(content)

    def new_chunk(self, size=None, content=b"", flags=PT_R|PT_W|PT_X):
        if size is None:
            size = len(content)

        for chunk in self._chunks:
            #Do a try catch because Chunk manager creates exceptions when sizes or flags don't match
            try:
                new_chunk = chunk.new_chunk(size=size, flags=flags, content=content)
                #If no exception, then succeded, return
                return new_chunk
            #errorn in adding chunk, pass
            except Exception as e:
                # print(e)
                pass

        #No chunks could satisfy the request

        page_aligned_size = (size & -0x1000) + 0x1000
        #Page aligned size so we can use it wisely for future chunks too and do not end up wasting virtual address space

        new_segment = self.new_segment(size=page_aligned_size, flags=flags)

        managed_chunk = ChunkManager(new_segment)
        self._chunks.append(managed_chunk)
        
        return managed_chunk.new_chunk(size=size, content=content, flags=flags) 
 
                











            
