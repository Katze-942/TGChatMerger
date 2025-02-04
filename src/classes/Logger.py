from datetime import datetime
import config

class Logger:
    """Используется для вывода сообщений в терминал.
    Поддерживает окрашивание текста и фильтрацию по уровням детализации.
    """

    color = getattr(config, 'CONSOLE_COLOR', True)
    level_detail = int(getattr(config, 'CONSOLE_LEVEL_DETAIL', 3))

    # ANSI escape-коды для цветов
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RESET = "\033[0m"  # Сброс цвета

    def __init__(self, *labels: str):
        """Создаёт логгер с начальными метками.

        Пример:
        ```python
        loggerTest = Logger("LABEL1", "LABEL2")
        loggerTest.info(2, "Информационное сообщение")
        # [18:00:42] [LABEL1] [LABEL2]: Информационное сообщение
        ```
        """

        self.labels_str = " ".join(f"[{label}]" for label in labels) + ":"
        """Метки в начале строки ([LABEL1] [LABEL2] и так далее)"""

    def _get_current_time(self) -> str:
        return datetime.now().strftime("[%H:%M:%S]")

    def log(self, level: int, text: str, preLabel: str, color: str | None = None):
        if Logger.level_detail >= level:
            time_str = self._get_current_time()

            if Logger.color and color:
                print(f"{color}{time_str} {preLabel} {self.labels_str} {text}{Logger.RESET}")
            else:
                print(f"{time_str} {preLabel} {self.labels_str} {text}")

    def info(self, level: int, text: str):
        """Обычное информационное сообщение."""
        self.log(level, text, '[INFO]')

    def ok(self, level: int, text: str):
        """Сообщение с успешным выполнением чего-либо."""
        self.log(level, text, '[GOOD]', Logger.GREEN)

    def warn(self, text: str):
        """Сообщение с предупреждением. Устанавливается level_detail=1"""
        self.log(1, text, '[WARN]', Logger.YELLOW)

    def error(self, text):
        """Сообщение с ошибкой. Устанавливается level_detail=1"""
        self.log(1, text, '[ERROR]', Logger.RED)
