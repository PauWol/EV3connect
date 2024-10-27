import logging
import sys
import os

from art import text2art
from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)


class Logger:
    LOG_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def __init__(self, name: str, debug: bool = False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self._setup_console_handler()

    def _setup_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # Custom formatter to add colors to log levels
        formatter = self.ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(console_handler)

    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            log_color = Logger.LOG_COLORS.get(record.levelno, Fore.WHITE)
            log_message = super().format(record)
            return f"{log_color}{log_message}{Style.RESET_ALL}"

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
    
def information():
    ev3_graffiti = text2art("EV3", font="graffiti", chr_ignore=True)
    print(f"{Fore.RED}{ev3_graffiti}{Style.RESET_ALL}\n\n")
    print(f"{Fore.CYAN}EV3 Console version 1.0\n-----------------------\nLogs will be shown here\n\n{Style.RESET_ALL}")

def resolve_path(file,relative_path):
    """
    Resolves the path to the given relative path.

    Args
    ----
    relative_path: str
        The relative path to resolve.

    Returns
    -------
    str
        The resolved path.
    """
    logger = Logger("path_resolve", debug=False)
    try:
        return os.path.join(os.path.dirname(file), relative_path)
    except NameError:
        logger.warning(f"Failed to resolve path: {relative_path}")
        return relative_path