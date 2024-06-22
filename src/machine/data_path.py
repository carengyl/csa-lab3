from typing import List, Dict

from machine.isa_model import Opcode
from machine.signals import Signal, Operands


class DataPath:
    VALUE_WIDTH = 32
    VALUE_MIN = -2 ** (VALUE_WIDTH - 1)
    VALUE_MAX = 2 ** (VALUE_WIDTH - 1) - 1

    data_memory_size: int
    data_memory: List[int]
    acc: int
    buf_reg: int
    stack_pointer: int
    address_reg: int
    flags: Dict[str, bool]
    alu_out: int
    memory_out: int

    input_buffer: List[int]
    output_buffer: List[int]

    def __init__(self,
                 memory_capacity: int,
                 input_buffer: List[int]):
        if not memory_capacity > 0:
            raise ValueError("Data memory capacity must be greater than zero.")

        self.data_memory_size = memory_capacity
        self.data_memory = [0] * memory_capacity
        self.acc = 0
        self.buf_reg = 0
        self.stack_pointer = 0
        self.address_reg = 0
        self.alu_out = 0
        self.memory_out = 0

        self.input_buffer = input_buffer
        self.output_buffer = []
        self.flags = {
            'Z': False,
            'N': False
        }

    def signal_latch_acc(self, sel, load=0):
        self.acc = load if sel == Signal.DIRECT_ACC_LOAD else self.alu_out

    def signal_latch_address(self, sel, load=0):
        self.address_reg = load if sel == Signal.DIRECT_ADDRESS_LOAD else self.alu_out

    def memory_manager(self, operation):
        if operation == Signal.READ:
            self.memory_out = self.data_memory[self.address_reg]
        elif operation == Signal.WRITE:
            self.data_memory[self.address_reg] = self.alu_out

    def signal_latch_regs(self, *regs):
        if Signal.BUF_LATCH in regs:
            self.buf_reg = self.alu_out
        if Signal.STACK_LATCH in regs:
            self.stack_pointer = self.alu_out

    def execute_alu_operation(self, operation, value=0):
        match operation:
            case Opcode.ADD:
                return self.alu_out + value
            case Opcode.SUB:
                return self.alu_out - value
            case Opcode.MUL:
                return self.alu_out * value
            case Opcode.DIV:
                return self.alu_out // value
            case Opcode.REM:
                return self.alu_out % value
            case Opcode.INC:
                return self.alu_out + 1
            case Opcode.DEC:
                return self.alu_out - 1
            case Opcode.CMP:
                self.flags = {"z": self.alu_out == value,
                              "n": self.alu_out < value}
                return self.alu_out
            case Opcode.MOVH:
                return self.alu_out << 24

    def get_bus_value(self, bus):
        match bus:
            case Operands.ACC:
                return self.acc
            case Operands.BUF:
                return self.buf_reg
            case Operands.STACK:
                return self.stack_pointer
            case Operands.MEM:
                return self.memory_out

    def alu_working(self, operation=Opcode.ADD, valves=None):
        if valves is None:
            valves = [Operands.ACC]
        self.alu_out = self.get_bus_value(valves[0])
        if Operands.ACC in valves:
            self.flags = {"z": self.acc == 0, "n": self.alu_out < 0}
        if operation in [Opcode.INC, Opcode.DEC, Opcode.MOVH]:
            self.alu_out = self.execute_alu_operation(operation)
        elif len(valves) > 1:
            self.alu_out = self.execute_alu_operation(operation, self.get_bus_value(valves[1]))
