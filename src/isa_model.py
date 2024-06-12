import json
from enum import Enum
from typing import NamedTuple, List, Dict


class Opcode(str, Enum):
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


class Term(NamedTuple):
    line: int
    pos: int
    symbol: str


def write_instructions(filename: str,
                       instructions: List[Dict[str, int | Opcode | Term]]) -> None:
    """
    Writes instructions into a file.

    :param filename: path to output JSON file.
    :param instructions: instructions to write.
    """
    with open(filename, "w", encoding="utf-8") as file:
        buffer: List[str] = []
        for instructions in instructions:
            buffer.append(json.dumps(instructions))

        file.write("[" + ",\n ".join(buffer) + "]")


def read_code(filename: str) -> List[Dict[str, int | Opcode | Term]]:
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())

    for instr in code:
        # String to Opcode
        instr["opcode"] = Opcode(instr["opcode"])

        # term list to class Term
        if "term" in instr:
            assert len(instr["term"]) == 3
            instr["term"] = Term(instr["term"][0], instr["term"][1], instr["term"][2])

    return code


def get_arg_num(opcode: str) -> int:
    """
    Returns number of args for opcode.

    :param opcode: opcode string.
    :return: number of args.
    """
    if opcode in [Opcode.JZ, Opcode.JUMP]:
        return 1
    else:
        return 0
