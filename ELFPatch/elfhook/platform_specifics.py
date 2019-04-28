from collections import namedtuple


class Arch:

    def __init__(self, assembler):
        self.assembler = assembler


class I386(Arch):

    def save_registers(self):
        return self.assembler.assemble('''
            pushfd
            push ebp
            push esi
            push edi
            push edx
            push ecx
            push ebx
            push eax
            push esp
        ''')

    def restore_registers(self):
        return self.assembler.assemble('''
            add esp, 4
            pop eax
            pop ebx
            pop ecx
            pop edx
            pop edi
            pop esi
            pop ebp
            popfd
        ''')

    def zero_registers(self):
        return self.assembler.assemble('''
            xor eax, eax
            xor ebx, ebx
            xor ecx, ecx
            xor edx, edx
            xor edi, edi
            xor esi, esi
            xor ebp, ebp
            push eax
            popfd
        ''')

    def save_stackpointer(self, offset):
        offset &= 0xffffffffffffffff
        return self.assembler.assemble(f'''
            mov [rip + 0x{offset:x} - 7], rsp
        ''')

    def restore_stackpointer(self, offset):
        offset &= 0xffffffffffffffff
        return self.assembler.assemble(f'''
            mov rsp, [rip + 0x{offset:x} - 7]
        ''')

    def relative_call(self, offset):
        offset &= 0xffffffffffffffff
        return self.assembler.assemble(f'''
            call 0x{offset:x}
        ''')

    def relative_jump(self, offset):
        offset &= 0xffffffffffffffff
        return self.assembler.assemble(f'''
            jmp 0x{offset:x}
        ''')

    def fake_initial_stack(self):
        return self.assembler.assemble(f'''
            # align stack
            and rsp, 0xfffffffffffffff0

            # save rax
            push rax

            # fake arg
            push 0x6b6f6f68

            # fake env entry
            mov rax, 0x42423d4141
            push rax

            # random bytes for AT_RANDOM
            push 0
            push 0
            mov rax, rsp

            # auxv: AT_NULL, AT_RANDOM
            push 0
            push 0
            push rax
            push 25

            # env
            push 0
            lea rax, [rsp + 0x38]
            push rax

            # delim
            push 0

            # argv, argc
            lea rax, [rsp + 0x50]
            push rax
            push 1

            # restore rax
            mov rax, [rsp + 0x68]
        ''')

    def swap_fs_base(self, offset):
        offset &= 0xffffffffffffffff
        return self.assembler.assemble(f'''
            # save rbx
            push rbx

            call A
        A:
            pop rbx
            add rbx, 0x{offset:x} - 6

            # save other registers
            push rax
            push rdi
            push rsi

            # arch_prctl(ARCH_GET_FS, rsp)
            mov rax, 0x9e
            mov rdi, 0x1003
            sub rsp, 8
            mov rsi, rsp
            syscall
            test rax, rax
            jz L1
            int3
        L1:

            # arch_prctl(ARCH_SET_FS, *offset)
            mov rax, 0x9e
            mov rdi, 0x1002
            mov rsi, [rbx]
            syscall
            test rax, rax
            jz L2
            int3
        L2:

            # save overwritten FS in *offset
            pop rax
            mov [rbx], rax

            # restore registers
            pop rsi
            pop rdi
            pop rax
            pop rbx
        ''')


class Amd64(Arch):

    def save_registers(self):
        return self.assembler.assemble('''
            pushfq
            push r15
            push r14
            push r13
            push r12
            push r11
            push r10
            push r9
            push r8
            push rbp
            push rsi
            push rdi
            push rdx
            push rcx
            push rbx
            push rax
            mov rdi, rsp
        ''')

    def restore_registers(self):
        return self.assembler.assemble('''
            pop rax
            pop rbx
            pop rcx
            pop rdx
            pop rdi
            pop rsi
            pop rbp
            pop r8
            pop r9
            pop r10
            pop r11
            pop r12
            pop r13
            pop r14
            pop r15
            popfq
        ''')

    def zero_registers(self):
        return self.assembler.assemble('''
            xor rax, rax
            xor rbx, rbx
            xor rcx, rcx
            xor rdx, rdx
            xor rdi, rdi
            xor rsi, rsi
            xor rbp, rbp
            xor r8, r8
            xor r9, r9
            xor r10, r10
            xor r11, r11
            xor r12, r12
            xor r13, r13
            xor r14, r14
            xor r15, r15
            push rax
            popfq
        ''')

    def save_stackpointer(self, offset):
        offset &= 0xffffffffffffffff
        return self.assembler.assemble(f'''
            mov [rip + 0x{offset:x} - 7], rsp
        ''')

    def restore_stackpointer(self, offset):
        offset &= 0xffffffffffffffff
        return self.assembler.assemble(f'''
            mov rsp, [rip + 0x{offset:x} - 7]
        ''')

    def relative_call(self, offset):
        offset &= 0xffffffffffffffff
        return self.assembler.assemble(f'''
            call 0x{offset:x}
        ''')

    def relative_jump(self, offset):
        offset &= 0xffffffffffffffff
        return self.assembler.assemble(f'''
            jmp 0x{offset:x}
        ''')

    def fake_initial_stack(self):
        return self.assembler.assemble(f'''
            # align stack
            and rsp, 0xfffffffffffffff0

            # save rax
            push rax

            # fake arg
            push 0x6b6f6f68

            # fake env entry
            mov rax, 0x42423d4141
            push rax

            # random bytes for AT_RANDOM
            push 0
            push 0
            mov rax, rsp

            # auxv: AT_NULL, AT_RANDOM
            push 0
            push 0
            push rax
            push 25

            # env
            push 0
            lea rax, [rsp + 0x38]
            push rax

            # delim
            push 0

            # argv, argc
            lea rax, [rsp + 0x50]
            push rax
            push 1

            # restore rax
            mov rax, [rsp + 0x68]
        ''')

    def swap_fs_base(self, offset):
        offset &= 0xffffffffffffffff
        return self.assembler.assemble(f'''
            # save rbx
            push rbx

            call A
        A:
            pop rbx
            add rbx, 0x{offset:x} - 6

            # save other registers
            push rax
            push rdi
            push rsi

            # arch_prctl(ARCH_GET_FS, rsp)
            mov rax, 0x9e
            mov rdi, 0x1003
            sub rsp, 8
            mov rsi, rsp
            syscall
            test rax, rax
            jz L1
            int3
        L1:

            # arch_prctl(ARCH_SET_FS, *offset)
            mov rax, 0x9e
            mov rdi, 0x1002
            mov rsi, [rbx]
            syscall
            test rax, rax
            jz L2
            int3
        L2:

            # save overwritten FS in *offset
            pop rax
            mov [rbx], rax

            # restore registers
            pop rsi
            pop rdi
            pop rax
            pop rbx
        ''')


platforms = {
    0x03: I386,
    0x3e: Amd64,
}
