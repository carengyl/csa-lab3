class Signal:
    DIRECT_ACC_LOAD = "direct acc load"
    DATA_ACC_LOAD = "data acc load"
    DIRECT_ADDRESS_LOAD = "direct address load"
    DATA_ADDRESS_LOAD = "data address load"

    WRITE = "write"
    READ = "read"

    STACK_LATCH = "stack_latch"
    BUF_LATCH = "buf_latch"

    NEXT_IP = "next ip"
    JMP_ARG = "jmp arg"
    DATA_IP = "data ip"


class Operands:
    ACC = "acc"
    MEM = "mem"
    BUF = "buf"
    STACK = "stack"
