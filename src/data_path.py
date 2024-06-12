import logging
from typing import List

from isa_model import Opcode


class DataPath:
    data_memory_size: int
    data_memory: List[int]
    data_address: int
    acc: int
    input_buffer = None
    output_buffer: List[str]

    def __init__(self, data_memory_size, input_buffer):
        if not data_memory_size > 0:
            raise ValueError("Data memory must be greater than zero.")

        self.data_memory_size = data_memory_size
        self.data_memory = [0] * data_memory_size
        self.data_address = 0
        self.acc = 0
        self.input_buffer = input_buffer
        self.output_buffer = []

    def signal_latch_data_addr(self, sel):
        if sel not in (Opcode.LEFT.value, Opcode.RIGHT.value):
            raise ValueError(f"Internal error, incorrect selector: {sel}")

        if sel == Opcode.LEFT.value:
            self.data_address -= 1
        elif sel == Opcode.RIGHT.value:
            self.data_address += 1

        if not (0 <= self.data_address < self.data_memory_size):
            raise MemoryError(f"Out of memory: {self.data_memory_size}")

    def signal_latch_acc(self):
        self.acc = self.data_memory[self.data_address]

    def signal_wr(self, sel):
        if sel not in (Opcode.INC.value,
                       Opcode.DEC.value,
                       Opcode.INPUT.value):
            raise ValueError(f"Internal error, incorrect selector: {sel}")

        if sel == Opcode.INC.value:
            self.data_memory[self.data_address] = self.acc + 1
            if self.data_memory[self.data_address] == 128:
                self.data_memory[self.data_address] = -128

        elif sel == Opcode.DEC.value:
            self.data_memory[self.data_address] = self.acc - 1
            if self.data_memory[self.data_address] == -129:
                self.data_memory[self.data_address] = 127

        elif sel == Opcode.INPUT.value:
            if len(self.input_buffer) == 0:
                raise EOFError()
            symbol = self.input_buffer.pop(0)
            symbol_code = ord(symbol)
            assert -128 <= symbol_code <= 127, "input token is out of bound: {}".format(symbol_code)
            self.data_memory[self.data_address] = symbol_code
            logging.debug("input: %s", repr(symbol))

    def signal_output(self):
        symbol = chr(self.acc)
        logging.debug("output: %s << %s", repr("".join(self.output_buffer)), repr(symbol))
        self.output_buffer.append(symbol)

    def zero(self):
        return self.acc == 0
