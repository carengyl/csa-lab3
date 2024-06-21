import json
from enum import Enum
from typing import NamedTuple, List, Dict


class Opcode(str, Enum):
    INC = "inc"
    DEC = "dec"
    HALT = "halt"
    POP = "pop"
    PUSH = "push"
    RET = "ret"
    MOVH = "movh"
    INPUT = "input"
    PRINT = "print"
    LOAD = "load"
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    REM = "rem"
    CMP = "cmp"
    STORE = "store"
    JMP = "jmp"
    JE = "je"
    JNE = "jne"
    JGE = "jge"
    CALL = "call"

    OP_0 = {INC, DEC, HALT, POP, PUSH, RET, INPUT, PRINT, MOVH}  # Безадресные команды
    OP_1 = {LOAD, ADD, SUB, MUL, DIV, REM, CMP}  # Адресные команды с прямой загрузкой
    OP_2 = {STORE}  # Адресные команды без прямой загрузки
    OP_3 = {JMP, JE, JNE, JGE, CALL}  # Команды ветвления

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


def get_arg_num(opcode: Opcode) -> int:
    """
    Returns number of args for Opcode.

    :param opcode: opcode string.
    :return: number of args.
    """
    if opcode.value in Opcode.OP_1 or opcode.value in Opcode.OP_2 or opcode.value in Opcode.OP_3:
        return 1
    else:
        return 0
