import pathlib
import re
import sys
from typing import Tuple, Union

from machine.isa_model import *

type LABELS_DICT = Dict[str, int]  # Internal type for dictionary with labels and instruction index
type INSTRUCTIONS_LIST = List[Dict[str, Union[int, Opcode, str]]]  # Internal type for list of instructions


def preprocess_text(text: str) -> Tuple[LABELS_DICT, INSTRUCTIONS_LIST]:
    """
    Preprocesses the assembly text to extract labels and instructions.

    :param text: Assembly code as a string.
    :return: Labels as dictionary and instructions as a list of dictionaries.
    """
    instructions: INSTRUCTIONS_LIST = []
    labels: LABELS_DICT = {}

    for line_number, line in enumerate(text.splitlines(), start=1):
        token: str = line.split(";", 1)[0].strip()

        if token == "":
            continue

        opcode_pointer = len(instructions)

        if token.endswith(":"):
            label = token.strip(":")
            if label in labels:
                raise ValueError(f"Redefinition of label: {label}")
            labels[label] = opcode_pointer

        elif " " in token:
            sub_tokens: List[str] = token.split(" ", 1)

            if len(sub_tokens) != 2:
                raise ValueError(f"Invalid instruction: {token}")

            mnemonic, arg = sub_tokens
            opcode = Opcode(mnemonic)

            if get_arg_num(opcode) != 1:
                raise ValueError(f"Invalid argument: {arg}")

            # Прямая загрузка числа
            if ((arg.isdigit() or (arg.startswith('-') and arg[1:].isdigit()))
                    and opcode in Opcode.OP_1):
                arg = int(arg)

            # Прямая загрузка символа
            elif (len(arg) == 3 and arg.startswith("'") and arg.endswith("'")
                  and opcode in Opcode.OP_1):
                arg = ord(arg[1:-1])

            # Абсолютная, косвенная или косвенная автоинкрементная адресация
            elif (re.match(r"\*{1,2}\d+\+?", arg)
                  and (opcode in Opcode.OP_1 or opcode in Opcode.OP_2)):
                arg = arg

            # Переход по метке
            elif (re.match(r"[a-zA-z0-9_]+", arg)
                  and (opcode in Opcode.OP_3)):
                arg = arg

            # Default case
            else:
                raise ValueError(f"Invalid argument: {arg} for instruction: {opcode}")

            instructions.append({"index": opcode_pointer,
                                 "opcode": opcode,
                                 "arg": arg})

        else:
            opcode = Opcode(token)
            if opcode not in Opcode.OP_0:
                raise ValueError(f"Invalid usage: {token}")

            instructions.append({"index": opcode_pointer,
                                 "opcode": opcode})

    return labels, instructions


def assign_labels(labels: LABELS_DICT,
                  instructions: INSTRUCTIONS_LIST) -> INSTRUCTIONS_LIST:
    """
    Assigns labels to the instructions.

    :param labels: Labels as a dictionary.
    :param instructions: Instructions as a list of dictionaries.
    :return: Labeled instructions as a list of dictionaries.
    """
    for instruction in instructions:
        if "arg" in instruction.keys():
            argument = instruction["arg"]

            if type(argument) is int:  # Прямая загрузка
                continue

            if argument.startswith("*"):  # Абсолютная, косвенная или косвенная автоинкрементная адресация
                continue

            if argument not in labels:
                raise ValueError(f"Label not defined: {argument}")

            instruction["arg"] = labels[argument]

    return instructions


def translate_file(source: str) -> INSTRUCTIONS_LIST:
    """
    Translates the assembly code into a list of instructions.

    :param source: Assembly code as a string.
    :return: List of instructions as a list of dictionaries.
    """
    labels, instructions = preprocess_text(source)

    return assign_labels(labels, instructions)


def main(input_file: str,
         output_file: str) -> None:
    """
    Main function that reads the assembly code and translates it into a list of instructions.

    :param input_file: Path to the input assembly file.
    :param output_file: Path to the output JSON file.
    """
    in_path = pathlib.Path(input_file)
    out_path = pathlib.Path(output_file)

    if not (in_path.is_file() and in_path.suffix == ".asm"):
        raise FileNotFoundError(f"Invalid input file or file does not exist: expected <input path>.asm")

    if not (out_path.is_file() and out_path.suffix == ".json") and out_path.exists():
        raise FileExistsError(f"Invalid output file: expected <output path>.json")

    with open(input_file, "r") as f:
        source = f.read()

    instructions = translate_file(source)
    write_instructions(output_file, instructions)
    print(f"source LoC: {len(source.splitlines())}, instruction codes: {len(instructions)}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: translator.py <input file> <output file>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    main(input_path, output_path)
