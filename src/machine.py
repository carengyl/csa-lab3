import logging
import sys
from typing import Tuple, List, Dict

from isa_model import read_code, Opcode, Term


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


class ControlUnit:
    program: List[Dict[str, int | Opcode | Term]]
    program_counter: int
    data_path: DataPath
    _tick: int

    def __init__(self, program: List[Dict[str, int | Opcode | Term]], data_path: DataPath):
        self.program = program
        self.program_counter = 0
        self.data_path = data_path
        self._tick = 0

    def tick(self):
        self._tick += 1

    def current_tick(self) -> int:
        return self._tick

    def signal_latch_program_counter(self, sel_next: bool):
        if sel_next:
            self.program_counter += 1
        else:
            instr = self.program[self.program_counter]
            assert "arg" in instr, "internal error"
            self.program_counter = instr["arg"]

    def decode_and_execute_control_flow(self, instr, opcode):
        if opcode is Opcode.HALT:
            raise StopIteration()

        if opcode is Opcode.JUMP:
            addr = instr["arg"]
            self.program_counter = addr
            self.tick()

            return True

        if opcode is Opcode.JZ:

            self.data_path.signal_latch_acc()
            self.tick()

            if self.data_path.zero():
                self.signal_latch_program_counter(sel_next=False)
            else:
                self.signal_latch_program_counter(sel_next=True)
            self.tick()

            return True

        return False

    def decode_and_execute(self):
        instr = self.program[self.program_counter]
        opcode = instr["opcode"]

        if self.decode_and_execute_control_flow(instr, opcode):
            return

        if opcode in {Opcode.RIGHT, Opcode.LEFT}:
            self.data_path.signal_latch_data_addr(opcode.value)
            self.signal_latch_program_counter(sel_next=True)
            self.tick()

        elif opcode in {Opcode.INC, Opcode.DEC, Opcode.INPUT}:
            self.data_path.signal_latch_acc()
            self.tick()

            self.data_path.signal_wr(opcode.value)
            self.signal_latch_program_counter(sel_next=True)
            self.tick()

        elif opcode is Opcode.PRINT:
            self.data_path.signal_latch_acc()
            self.tick()

            self.data_path.signal_output()
            self.signal_latch_program_counter(sel_next=True)
            self.tick()

    def __repr__(self):
        state_repr = "TICK: {:3} PC: {:3} ADDR: {:3} MEM_OUT: {} ACC: {}".format(
            self._tick,
            self.program_counter,
            self.data_path.data_address,
            self.data_path.data_memory[self.data_path.data_address],
            self.data_path.acc,
        )

        instr = self.program[self.program_counter]
        opcode = instr["opcode"]
        instr_repr = str(opcode)

        if "arg" in instr:
            instr_repr += " {}".format(instr["arg"])

        if "term" in instr:
            term = instr["term"]
            instr_repr += "  ('{}'@{}:{})".format(term.symbol, term.line, term.pos)

        return "{} \t{}".format(state_repr, instr_repr)


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
