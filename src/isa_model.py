from enum import Enum
from typing import NamedTuple


class OperationCode(str, Enum):
    RIGHT = "right"
    LEFT = "left"
    INC = "inc"
    DEC = "dec"
    INPUT = "input"
    PRINT = "print"

    JUMP = "jmp"
    JZ = "jz"
    HALT = "halt"

    def __str__(self):
        return self.value


def get_arg_num(opcode: str) -> int:
    if opcode in [OperationCode.JZ, OperationCode.JUMP]:
        return 1
    else:
        return 0


class Term(NamedTuple):
    line: int
    pos: int
    symbol: str
