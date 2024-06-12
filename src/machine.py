import logging
import sys
from typing import Tuple, List, Dict

from control_unit import ControlUnit
from data_path import DataPath
from isa_model import read_code, Opcode, Term


def simulation(code: List[Dict[str, int | Opcode | Term]],
               input_tokens: List[str],
               data_memory_size: int = 100,
               limit: int = 1000) -> Tuple[str, int, int]:
    data_path = DataPath(data_memory_size, input_tokens)
    control_unit = ControlUnit(code, data_path)
    instr_counter = 0

    logging.debug("%s", control_unit)
    try:
        while instr_counter < limit:
            control_unit.decode_and_execute()
            instr_counter += 1
            logging.debug("%s", control_unit)

    except EOFError:
        logging.warning("Input buffer is empty.")
    except StopIteration:
        pass

    if instr_counter >= limit:
        logging.warning("Limit exceeded.")

    logging.info("output_buffer: %s", repr("".join(data_path.output_buffer)))

    return "".join(data_path.output_buffer), instr_counter, control_unit.current_tick()


def main(source: str, target: str):
    code = read_code(source)
    with open(target, "r") as f:
        input_text = f.read()
        input_tokens = []
        for char in input_text:
            input_tokens.append(char)
        logging.debug(input_tokens)

    output, instr_counter, ticks = simulation(code, input_tokens)
    print("".join(output))
    print(f"instr_counter: {instr_counter} ticks: {ticks}")


if __name__ == '__main__':
    logger = logging.getLogger()
    if not 3 <= len(sys.argv) <= 4:
        print('Usage: python machine.py <code file> <input file> [OPTIONS]')
        sys.exit(1)

    code_file = sys.argv[1]
    input_file = sys.argv[2]
    options = sys.argv[3:]

    if "-d" in options or "--debug" in options:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    main(code_file, input_file)
