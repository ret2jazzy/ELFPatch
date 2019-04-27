#include <stdint.h>

#define HOOK(addr) __attribute__((cdecl)) void hook_##addr(state_t *state)
#define INIT() static void _main_init(void)

static void _main_init(void);

void _main_end(void) {
    asm("");
}

int main(void) {
    _main_init();
    _main_end();
    return 0;
}

// ---------- amd64 ----------

#if defined(__x86_64__) || defined(_M_X64)

typedef struct {
    uint64_t rax;
    uint64_t rbx;
    uint64_t rcx;
    uint64_t rdx;
    uint64_t rdi;
    uint64_t rsi;
    uint64_t rbp;
    uint64_t r8;
    uint64_t r9;
    uint64_t r10;
    uint64_t r11;
    uint64_t r12;
    uint64_t r13;
    uint64_t r14;
    uint64_t r15;
    uint64_t rflags;
    uint64_t redzone[16];
    uint64_t stack[];
} state_t;

// ---------- i386 ----------

#elif defined(__i386) || defined(_M_IX86)

typedef struct {
    uint32_t eax;
    uint32_t ebx;
    uint32_t ecx;
    uint32_t edx;
    uint32_t edi;
    uint32_t esi;
    uint32_t ebp;
    uint32_t eflags;
    uint32_t stack[];
} state_t;

#else
#error "Unsupported architecture"
#endif
