import json
import pathlib
import sys
from typing import List, Dict
from isa_model import OperationCode, Term, get_arg_num


def preprocess_text(text: str) -> (Dict[str, int],
                                   List[Dict[str, int | OperationCode | Term]]):
    instructions: List[Dict[str, int | OperationCode | Term]] = []
    labels: Dict[str, int] = {}

    for line_number, line in enumerate(text.splitlines(), start=1):
        token: str = line.split(";", 1)[0].strip()

        if token == "":
            continue

        opcode_pointer = len(instructions)

        if token.endswith(":"):
            label = token.strip(":")
            assert label not in labels, f"Redefinition of label: {label}"
            labels[label] = opcode_pointer

        elif " " in token:
            sub_tokens: List[str] = token.split(" ")
            assert len(sub_tokens) == 2, f"Invalid instruction: {token}"

            mnemonic: str
            arg: str
            mnemonic, arg = sub_tokens

            opcode = OperationCode(mnemonic)

            assert get_arg_num(opcode) == 1, f"Invalid argument: {arg}"

            instructions.append({"index": opcode_pointer,
                                 "opcode": opcode,
                                 "arg": arg,
                                 "term": Term(line_number, 0, token)})

        else:
            opcode = OperationCode(token)
            instructions.append({"index": opcode_pointer,
                                 "opcode": opcode,
                                 "term": Term(line_number, 0, token)})

    return labels, instructions


def assign_labels(labels: Dict[str, int],
                  instructions: List[Dict[str, int | OperationCode | Term]]) -> List[Dict[str, int | OperationCode | Term]]:
    for instruction in instructions:
        if "arg" in instruction.keys():
            label = instruction["arg"]
            assert label in labels, f"Label not defined: {label}"
            instruction["arg"] = labels[label]

    return instructions


def translate_file(source: str) -> List[Dict[str, int | OperationCode | Term]]:
    labels: Dict[str, int]
    instructions: List[Dict[str, int | OperationCode | Term]]

    labels, instructions = preprocess_text(source)

    return assign_labels(labels, instructions)


def write_instructions(filename: str,
                       instructions: List[Dict[str, int | OperationCode | Term]]) -> None:
    with open(filename, "w", encoding="utf-8") as file:

        buffer: List[str] = []
        for instructions in instructions:
            buffer.append(json.dumps(instructions))

        file.write("[" + ",\n ".join(buffer) + "]")


def main(input_file: str,
         output_file: str) -> None:
    assert pathlib.Path(input_file).is_file() and pathlib.Path(input_file).suffix == ".asm", \
        "Invalid input file or file does not exist: expected <input path>.asm"
    assert ((pathlib.Path(output_file).is_file() and pathlib.Path(output_file).suffix == ".json") or
            (not pathlib.Path(output_file).exists())), \
        "Invalid output file: expected <output path>.json"

    with open(input_file, "r") as f:
        source: str = f.read()

    instructions: List[dict] = translate_file(source)

    write_instructions(output_file, instructions)
    print("source LoC:", len(source.split("\n")),
          "instruction codes:", len(instructions))


if __name__ == '__main__':
    assert len(sys.argv) == 3, "Wrong number of arguments: translator.py <input file> <output file>"
    input_path: str = sys.argv[1]
    output_path: str = sys.argv[2]
    main(input_path, output_path)
