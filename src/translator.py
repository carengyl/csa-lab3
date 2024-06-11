import pathlib
import sys
from typing import List, Dict, Tuple, Union

from isa_model import Opcode, Term, get_arg_num, write_instructions


def preprocess_text(text: str) -> Tuple[Dict[str, int], List[Dict[str, Union[int, Opcode, Term]]]]:
    """
    Preprocesses the assembly text to extract labels and instructions.

    :param text: Assembly code as a string.
    :return: Labels as dictionary and instructions as a list of dictionaries.
    """
    instructions: List[Dict[str, Union[int, Opcode, Term]]] = []
    labels: Dict[str, int] = {}

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
            sub_tokens: List[str] = token.split(" ")
            if len(sub_tokens) != 2:
                raise ValueError(f"Invalid instruction: {token}")

            mnemonic: str
            arg: str
            mnemonic, arg = sub_tokens

            opcode = Opcode(mnemonic)

            if get_arg_num(opcode) != 1:
                raise ValueError(f"Invalid argument: {arg}")

            instructions.append({"index": opcode_pointer,
                                 "opcode": opcode,
                                 "arg": arg,
                                 "term": Term(line_number, 0, token)})

        else:
            opcode = Opcode(token)
            instructions.append({"index": opcode_pointer,
                                 "opcode": opcode,
                                 "term": Term(line_number, 0, token)})

    return labels, instructions


def assign_labels(labels: Dict[str, int],
                  instructions: List[Dict[str, Union[int, Opcode, Term]]]) -> List[Dict[str, Union[int, Opcode, Term]]]:
    """
    Assigns labels to the instructions.

    :param labels: Labels as a dictionary.
    :param instructions: Instructions as a list of dictionaries.
    :return: Labeled instructions as a list of dictionaries.
    """
    for instruction in instructions:
        if "arg" in instruction.keys():
            label = instruction["arg"]
            if label not in labels:
                raise ValueError(f"Label not defined: {label}")
            instruction["arg"] = labels[label]

    return instructions


def translate_file(source: str) -> List[Dict[str, Union[int, Opcode, Term]]]:
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
