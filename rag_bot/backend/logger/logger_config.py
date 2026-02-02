import logging
import sys

logger1 = logging.getLogger(__name__)

logger1.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_formatter = logging.Formatter("%(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger1.addHandler(console_handler)

logger1.propagate = False