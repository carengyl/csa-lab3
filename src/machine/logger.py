import logging


class Logger:
    def __init__(self,
                 name,
                 log_type):
        self.code = name
        self.log_type = log_type

        with open(f"machine/logs/{log_type}.log", "w") as log:
            log.truncate(0)

        self.log = logging.getLogger(name)
        file_handler = logging.FileHandler(f"machine/logs/{log_type}.log", "w")
        formatter = logging.Formatter("%(levelname)s: %(message)s)")

        file_handler.setFormatter(formatter)
        self.log.addHandler(file_handler)
