from datetime import datetime

class Logger:
    """Используется для вывода сообщений в терминал.
    Поддерживает окрашивание текста и фильтрацию по уровням детализации.
    """

    color = False
    level_detail = 3

    # ANSI escape-коды для цветов
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RESET = '\033[0m' # Сброс цвета

    def __init__(self, *labels: str):
        """Создаёт логгер с начальными метками.
        
        Пример:
        ```python
        loggerTest = Logger("LABEL1", "LABEL2")
        loggerTest.info(2, "Информационное сообщение")
        # [18:00:42] [LABEL1] [LABEL2]: Информационное сообщение
        ```
        """

        self.labels_str=" ".join(f"[{label}]" for label in labels) + ':'
        """Метки в начале строки ([LABEL1] [LABEL2] и так далее)"""

    def _get_current_time(self) -> str:
        """Возвращает текущее время в формате [HH:MM:SS]."""
        return datetime.now().strftime("[%H:%M:%S]")

    def log(self, level: int, text: str, color:str|None=None):
        """Функция для вывода сообщения в терминал.
        Выводит сообщение в консоль, если его уровень >= текущего уровня детализации.

        :param level: Уровень от 1 до 3. Подробнее в config.py (`CONSOLE_LEVEL_DETAIL`)
        :param text: Текст сообщения
        :param color: ANSI код цвета
        """
        if level >= Logger.level_detail:
            time_str = self._get_current_time()

            if Logger.color:
                print(f"{color}{time_str} {self.labels_str}{Logger.RESET} {text}")
            else:
                print(f"{time_str} {self.labels_str} {text}")

    def info(self, level: int, text: str):
        """Обычное информационное сообщение.strptime
        
        :param level: Уровень от 1 до 3. Подробнее в config.py (`CONSOLE_LEVEL_DETAIL`)
        :param text: Текст сообщения
        """
        self.log(level, text)

    def ok(self, level: int, text: str):
        """Сообщение с успешным выполнением чего-либо. 
        
        :param level: Уровень от 1 до 3. Подробнее в config.py (`CONSOLE_LEVEL_DETAIL`)
        :param text: Текст сообщения
        """
        self.log(level, text, Logger.GREEN)

    def warn(self, text: str):
        """Сообщение с предупреждением. Устанавливается level_detail=1 
        
        :param text: Текст сообщения
        """
        self.log(1, text, Logger.YELLOW)

    def error(self, text):
        """Сообщение с ошибкой. Устанавливается level_detail=1 
        
        :param text: Текст сообщения
        """
        self.log(1, text, Logger.RED)

