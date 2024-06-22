import logging
from typing import List, Dict

from data_path import DataPath
from machine.decoder import Decoder
from machine.isa_model import Opcode
from machine.signals import Signal

ARITHMETIC_OPERATIONS = [Opcode.ADD, Opcode.SUB, Opcode.MUL,
                         Opcode.DIV, Opcode.REM, Opcode.INC,
                         Opcode.DEC, Opcode.CMP, Opcode.MOVH]


class ControlUnit:
    current_instruction: Dict[str, int | Opcode | str] | None
    instructions: List[Dict[str, int | Opcode | str]]
    ip: int
    instr_counter: int
    data_path: DataPath
    _tick: int

    def __init__(self,
                 program: List[Dict[str, int | Opcode | str]],
                 data_path: DataPath):
        self.log = logging.getLogger()
        self.current_instruction = None
        self.instructions = program
        self.ip = 0
        self.instr_counter = 0
        self.data_path = data_path
        self._tick = 0

    def tick(self):
        self._tick += 1

    def current_tick(self) -> int:
        return self._tick

    def execute(self):
        while self.instructions[self.ip]["opcode"] != Opcode.HALT:
            self.current_instruction = self.instructions[self.ip]
            self.instr_counter += 1
            decode = Decoder(self,
                             self.current_instruction["opcode"],
                             self.current_instruction["arg"] if "arg" in self.current_instruction else 0)

            signal = Signal.NEXT_IP

            if decode.opcode in [Opcode.LOAD, Opcode.STORE]:
                decode.decode_memory_commands()
            elif decode.opcode in ARITHMETIC_OPERATIONS:
                decode.decode_arithmetic_commands()
            elif decode.opcode in [Opcode.JMP, Opcode.JGE, Opcode.JE, Opcode.JNE]:
                signal = decode.decode_flow_commands()
            elif decode.opcode in [Opcode.CALL, Opcode.RET, Opcode.FUNC]:
                decode.decode_subprogram_commands()
            elif decode.opcode in [Opcode.PUSH, Opcode.POP]:
                decode.decode_stack_commands()

            if self.current_instruction["opcode"] not in [Opcode.CALL]:
                self.signal_latch_ip(signal, decode.arg)

            self.current_instruction = self.instructions[self.ip]
            self.log.debug(self, self._tick)

            return "".join([ascii(x) for x in self.data_path.output_buffer]), self.instr_counter, self._tick

    def signal_latch_ip(self, signal=Signal.NEXT_IP, arg=0):
        match signal:
            case Signal.NEXT_IP:
                self.ip += 1
            case Signal.JMP_ARG:
                self.ip = arg
            case Signal.DATA_IP:
                self.ip = self.data_path.alu_out

    def __repr__(self):
        return ""
