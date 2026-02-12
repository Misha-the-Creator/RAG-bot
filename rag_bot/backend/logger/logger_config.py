import logging
import sys

logger1 = logging.getLogger(__name__)
logger1.setLevel(logging.DEBUG)

# Форматтер — один для всех обработчиков
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Обработчик для консоли
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger1.addHandler(console_handler)

# Обработчик для файла
file_handler = logging.FileHandler("app.log", encoding="utf-8")  # можно указать любой путь, например: "/var/log/rag_bot.log"
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger1.addHandler(file_handler)

# Отключаем распространение (propagation), чтобы не дублировались логи, если есть root-логгер
logger1.propagate = False