import logging
import sys


def main(source: str, target: str):
    pass


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
