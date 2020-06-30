from .elfstructs import *
from . import structs as StructSkeletons 
from .elfparse import ELFParse
from .constants import *
from construct import *
from .segment import *
from .utils import page_start, page_end

class BasicELF:
    def __init__(self, ELFFile):
        with open(ELFFile, "rb") as f:
            self.rawelf = bytearray(f.read())

        self._init_structs()

        #Parse the ELF with the specific structs 
        self.elf = ELFParse(self._structs, self.rawelf)

        self._added_segments = []
        self._phdr_fixed = False
        # self._new_phdr_offset = None

    def write_file(self, filename):
        self._update_raw_elf()
        with open(filename, "wb") as f:
            f.write(self.rawelf)

    def new_segment(self, content=b"", flags=PT_R|PT_W|PT_X, type=PT_LOAD, size=None, align=0x1000, virtual_address=None, physical_off=None):
        if not self._phdr_fixed:
            self._phdr_fixed = True
            self._fix_phdr()

        if physical_off is not None and virtual_address is not None:
            physical_offset, virtual_addr = physical_off, virtual_address
        elif virtual_address is None and physical_off is not None:
            #TODO: Implement physical to virtual generation
            raise Exception("Cannot generate an segment with only physical offset")
        elif virtual_address is not None:
            physical_offset, virtual_addr = self._generate_physical_offset_for_virtual(virtual_address), virtual_address
        else:
            physical_offset, virtual_addr = self._generate_virtual_physical_offset_pair() 

        if size is None:
            size = len(content)+0x10

        #Create a raw segment struct using the Container from construct
        segment_struct = Container(p_type=type, p_flags=flags, p_offset=physical_offset, p_vaddr=virtual_addr,p_paddr=virtual_addr, p_filesz=size, p_memsz=size, p_align=align)

        self.elf.phdr_table.append(segment_struct)
        self.elf.ehdr.e_phnum += 1

        #Create a new segment class, but this time for segment addition
        segment_to_add = Segment(physical_offset, virtual_addr, size, flags=flags, align=align, content=content)
        self._added_segments.append(segment_to_add)

        return segment_to_add

    #Helper function to translate a virtual address to physical address
    def virtual_to_physical(self, virtual_address):
        for segment in self.elf.phdr_table:
            if virtual_address >= segment.p_vaddr and virtual_address < segment.p_vaddr+segment.p_memsz:
                address_offset = virtual_address - segment.p_vaddr
                physical_offset = address_offset + segment.p_offset
                return physical_offset

    #Weird issue with WSL is that it won't load overlapping segments even if they overlap only on the alignment (Linux kernel doesn't give a fuck if segments overlap, it just overwrites them)
    #if you have one segment from 0x0000 to 0x2000 with a 0x4000 alignment, WSL won't load a 2nd segment at 0x3000
    #Easy fix for that is to just change the alignment to 0x1000 (PAGE_SIZE) for every segment since that's what the kernel loads it as default
 #    def fix_WSL(self):
        # for phdr_entry in self.elf.phdr_table:
            # if phdr_entry.p_type == PT_LOAD:
                # phdr_entry.p_align = 0x1000

        # entry2 = self.elf.phdr_table[3]
        # entry_last = self.elf.phdr_table[-2]
        # self.elf.phdr_table[3] = entry_last
        # self.elf.phdr_table[-2] = entry2

    #Basically due to the weirdness of the loader and the kernel, the kernel believes the PHDR entry in memory would be at "FIRST_LOAD_SEGMENT + e_phoff", forwarding it to the loader, which is totally bizzare... Like what's the point of PHDR entry in the PHDR itself then?
    #Anyways, to cope with that, we try finding the smallest physical offset when loaded with the first segment itself would not conflict with any other segment's virtual addresses. It's a hacky approach but it works, so whatever...
    #Essentially we increase the size of the first loaded segment, so it loads the whole binary and then we change the PHDR and shit....
    #Even though the next segments might overlap with the first one (and overwrite), we only care that they don't overlap at the PHDR entry (and end up overwriting that)

    #UPDATE: Figured out a better way to do it without the overlapping segments byjust creating another LOAD segment at the end and aligning the FIRST_LOAD_SEGMENT + e_phoff with the new load segment

    #Basically we are trying to make the physical offset and the virtual address of EHDR match up so that e_phoff - FIRST_SEG.paddr  == vaddr_of_phoff - FIRST_SEG.vaddr

    def _fix_phdr(self):
        # Just an optimization, Try to find empty space between segments to hold the phdr and move it there
        size, physical_offset, virtual_addr, segment_ref = self._find_unused_space()
        if size >= 0x300:
            segment_ref.p_memsz += size
            segment_ref.p_filesz += size
            self._fix_pdhr_entry(physical_offset, virtual_addr, size=size)
            return

        #If it's not a dynamic binary, then we don't have the loader issue. We can just add a new segment for PHDR and load it there
        #Turns out LIBC_TLS also does the same thing as the kernel, which I explained above, so we can't do the special case for non dynamic libc
        # if not self._is_dynamic():
            #The reason I'm adding a new segment so that other segments after it don't end up taking the mem of the phdr
            # new_phdr = self.new_segment(size=0x1000, flags=PT_R|PT_W)
            # self._fix_pdhr_entry(new_phdr.physical_offset, new_phdr.virtual_address)
            # return

        #If large empty not available, then create a new segment (described in the comment above the function)
        #The hack commented out, figured out a better way
        # size_for_load_segment = physical_offset + 0x500

        #fix size for the first segment
#         for seg in self.elf.phdr_table:
            # #only for the first segment
            # if seg.p_type == PT_LOAD:
                # seg.p_filesz = size_for_load_segment
                # seg.p_memsz = size_for_load_segment + 0x10
                # break

        physical_offset, virtual_addr = self._find_non_conflicting_address_pair_for_phdr()

        new_phdr = self.new_segment(size=0x1000, flags=PT_R|PT_W, virtual_address=virtual_addr, physical_off=physical_offset)
        
        self._fix_pdhr_entry(physical_offset, virtual_addr)

        # self._new_phdr_offset = physical_offset + 0x500 

    #A function to find unused space between segments that can be used to hold the PHDR (should be > 0x500) 
    def _find_unused_space(self):
        all_load_segs = [X for X in self.elf.phdr_table if X.p_type == PT_LOAD]
        first_seg = all_load_segs[0]
        all_load_segs.sort(key=(lambda X:X.p_offset))

        largest_unused_space, poff, vaddr, segment_ref = -1, -1, -1, None
        #Essentially go through all the segments in sorted order and see if they have space in between (expects sane
        #non overlapping segments
        for idx in range(len(all_load_segs)-1):
            current_segment = all_load_segs[idx]
            current_segment_end_poff = current_segment.p_offset + current_segment.p_memsz
            current_segment_end_vaddr = current_segment.p_vaddr + current_segment.p_memsz

            next_segment = all_load_segs[idx+1]

            current_unused_space = next_segment.p_offset - current_segment_end_poff

            #Check if satisifes the check of being the correct offset away from the first load load segment 
            #As explained in the comment above the _fix_phdr function
            is_viable_for_phdr = (current_segment_end_poff - first_seg.p_offset) == (current_segment_end_vaddr - first_seg.p_vaddr)

            if is_viable_for_phdr and (current_unused_space > largest_unused_space):
                largest_unused_space = current_unused_space
                poff = current_segment_end_poff
                vaddr = current_segment_end_vaddr
                segment_ref = current_segment
        return largest_unused_space, poff, vaddr, segment_ref

    #Basically look for the smallest no conflicting address pair which can all be loaded as a part of the first segment
    def _find_non_conflicting_address_pair_for_phdr(self):
        all_load_segs = [X for X in self.elf.phdr_table if X.p_type == PT_LOAD]
    
        #The closest physical offset we can use
        closest_phy_offset = self._generate_physical_offset()
        #The base of the first LOAD segment
        virtual_base = all_load_segs[0].p_vaddr 

        #The minimum virtual address we would need to load upto to get the PHDR address in the first LOAD segment 
        virtual_min_addr = virtual_base + closest_phy_offset

        while self._is_conflicting_for_phdr(virtual_min_addr) or self._is_conflicting_for_phdr(virtual_min_addr+0x1000):
            #Just go to the next page boundry
            virtual_min_addr = page_end(virtual_min_addr)

        return virtual_min_addr - virtual_base, virtual_min_addr

    def _generate_physical_offset_for_virtual(self, virtual_address):
        virtual_offset_needed = virtual_address & 0xfff

        closest_physical = self._generate_physical_offset()

        if closest_physical&0xfff > virtual_offset_needed:
            closest_physical = (closest_physical & -0x1000) + 0x1000 + virtual_offset_needed
        else:
            closest_physical = (closest_physical & -0x1000) + virtual_offset_needed

        return closest_physical

    def _is_conflicting_for_phdr(self, address):
        #all load segments except the first one
        all_load_segs = [X for X in self.elf.phdr_table if X.p_type == PT_LOAD][1:]
        address = page_start(address)
        for seg in all_load_segs:
            #Just check if it's conflicting
            #using page_start because the there can be case when p_vaddr can be > address in the middle of the page 
            if address >= page_start(seg.p_vaddr) and address <= page_start(seg.p_vaddr + seg.p_memsz): 
                return True

        return False


    def _is_dynamic(self):
        for seg in self.elf.phdr_table:
            if seg.p_type == PT_INTERP:
                return True
        return False

    #Basically move the phdr to the bottom to make more space
    def _fix_pdhr_entry(self, offset, virt_addr, size=0x1000):
        self.elf.ehdr.e_phoff = offset

        for entry in self.elf.phdr_table:
            if entry.p_type == PT_PHDR:
                #Set the binary offset
                entry.p_offset = self.elf.ehdr.e_phoff
                #Set the virtual addresses 
                entry.p_vaddr = virt_addr 
                entry.p_paddr = virt_addr 
                #Set the size to a large-ish number
                entry.p_memsz = size
                entry.p_filesz = size

                break

    def _generate_virtual_physical_offset_pair(self):
       physical_offset = self._generate_physical_offset() 
       virtual_offset = self._generate_virtual_offset() + (physical_offset & (0xfff)) 
       #The binary is mapped in chunks of 0x1000 (the chunk which includes our physical offset will be mapped), so the LSBs of physical address and virtual offset should match.
       #So that out virt address falls in the right location when mapped as a whole chunk

       return physical_offset, virtual_offset


    def _generate_physical_offset(self):
        if len(self._added_segments) == 0:
            # if self._new_phdr_offset is not None:
                # return self._new_phdr_offset+0x10
            return (len(self.rawelf) & -0x10) + 0x10

        return ((self._added_segments[-1].physical_offset + self._added_segments[-1].size) & -0x10) + 0x10

    def _generate_virtual_offset(self):
        PAGE_SIZE = 0x1000

        #Get max virtual address mapped
        max_addr = max(self.elf.phdr_table, key=(lambda entry: (entry.p_vaddr + entry.p_memsz) if entry.p_type == PT_LOAD else 0)) 

        return (((max_addr.p_vaddr + max_addr.p_memsz) & -PAGE_SIZE) + PAGE_SIZE)

    def _init_structs(self):
        if self.rawelf[4] == 0x1: #4th byte identifies the ELF type
            self._bits = 32
        elif self.rawelf[4] == 0x2:
            self._bits = 64
        else:
            raise Exception("Not a valid 32/64 bit ELF")

        self._structs = ELFStructs()
            #Initialize the structures used based on the bitsize so we don't have to look them up everytime
        if self._bits == 32:
            self._structs.Elf_ehdr = StructSkeletons.Elf32_Ehdr 
            self._structs.Elf_phdr = StructSkeletons.Elf32_Phdr 
        else:
            self._structs.Elf_ehdr = StructSkeletons.Elf64_Ehdr 
            self._structs.Elf_phdr = StructSkeletons.Elf64_Phdr 

    def _update_raw_elf(self):
        # write the ELF header
        self.rawelf[0:self._structs.Elf_ehdr.sizeof()] = self._structs.Elf_ehdr.build(self.elf.ehdr) 

        #add the new updated LOAD segment's data in the ELF
        for segment in self._added_segments:
            segment_end = (segment.physical_offset + segment.size)
            if segment_end > len(self.rawelf):
                self.rawelf += b"\x00" * (segment_end - len(self.rawelf) + 1)
                self.rawelf[segment.physical_offset:segment.physical_offset+len(segment.content)] = segment.content

        # self._added_segments = []

        #get location of Phdr table (segement table) and size
        phdr_offset = self.elf.ehdr.e_phoff 
        phdr_size = self.elf.ehdr.e_phnum * self.elf.ehdr.e_phentsize
        phdr_end = phdr_offset + phdr_size

        #Check if Phdr table is after the end of the binary, and pad it with nulls if it is
        if phdr_end > len(self.rawelf):
            self.rawelf += b"\x00" * (phdr_end - len(self.rawelf)) 

        #Due to the limitations of the construct library (Not dynamic arrays), I create a new phdr_table struct to finally serialize the phdr in raw bytes
        self.rawelf[phdr_offset:phdr_end] = Array(self.elf.ehdr.e_phnum, self._structs.Elf_phdr).build(self.elf.phdr_table)



