from datetime import datetime
from enum import Enum

class LogLevel(Enum):
    ERROR_AND_WARN = 1
    INFO = 2
    DEBUG = 3

class CompressionType(Enum):
    ZIP_STORED = "ZIP_STORED"
    ZIP_DEFLATED = "ZIP_DEFLATED"
    ZIP_BZIP2 = "ZIP_BZIP2"
    ZIP_LZMA = "ZIP_LZMA"


### === Основные параметры === ###
PARSING_JSON=True
"""Включить парсинг JSON файла"""

PARSING_HTML=True
"""Включить парсинг HTML файлов"""

PATH_TD_EXPORTS=["ChatExport 2025-01-29-old"][0] # TODO: [0] является заглушкой
"""
Путь до других папок с экспортом Telegram чата.
Путь должен быть относительно того места, откуда запускается скрипт
"""

PATH_LATEST_TD_EXPORT="ChatExport 2025-01-29-new"
"""
Путь до экспорта Telegram чата, в котором сохранить изменения.
В этой директории будут изменяться файлы.
Путь должен быть относительно того места, откуда запускается скрипт
"""

### === Вывод в терминал === ###
CONSOLE_LEVEL_DETAIL=LogLevel.DEBUG
"""
Число от 0 до 3. Регулирует подробность выводимой информации
- LogLevel.ERROR_AND_WARN - будут выводиться только ошибки и предупреждения
- LogLevel.INFO - будут также выводиться и стадии, на которой скрипт работает
- LogLevel.DEBUG - будет выводиться и дополнительная информация
"""

CONSOLE_COLOR=True
"""Установите True для окрашивания логов"""

### === Резервное копирование === ###
BACKUP_FOLDER_PATH=f"{PATH_LATEST_TD_EXPORT}/Backup"
"""Путь, в котором будет сделана резервная копия HTML и JSON файлов"""

BACKUP_HTML_FILES=True
"""Включить резервную копия HTML файлов"""

BACKUP_JSON_FILE=True
"""Включить резервную копия JSON файла"""

BACKUP_REFLINK_USE=True
"""
Включите для использования REFLINK при копировании файлов.
Полезно, если у вас файловая система btrfs или другая CoW файловая система.
Для работы необходимо установить модуль reflink (https://reflink.readthedocs.io):
```bash
pip install reflink
```
"""

BACKUP_ARCHIVE=False
"""
По умолчанию создаётся резервная копия путём обычного копирования.
Установите True, если хотите сжать бэкап в один ZIP архив
"""

BACKUP_ARCHIVE_NAME=f"{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.zip"
"""Название ZIP-архива. Формат по умолчанию: 01-01-2025_00-00-00.zip"""

BACKUP_ARCHIVE_COMPRESSION=CompressionType.ZIP_LZMA
"""
Тип сжатия. Поддерживается:
- `CompressionType.ZIP_STORED` (без сжатия)
- `CompressionType.ZIP_DEFLATED` (стандартное сжатие)
- `CompressionType.ZIP_BZIP2` (сжатие через bzip2)
- `CompressionType.ZIP_LZMA` (сжатие через lzma)
"""

BACKUP_ARCHIVE_COMPRESS_LEVEL=9
"""Сила сжатия ZIP-архива от 1 до 9"""

### === ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ === ###
# В вашем Telegram экспорте могут быть сообщения от удалённых аккаунтов
# Если скрипт найдёт имя аккаунта в старых экспортах, то его имя можно будет восстановить
RESTORE_DELETED_ACCOUNTS_IN_HTML=False
"""Значение True восстанавливает названия аккаунтов в HTML файлах"""

RESTORE_DELETED_ACCOUNTS_IN_JSON=False
"""Значение True восстанавливает названия аккаунтов в JSON файле"""

# Противоположность предыдущего параметра. При True убирает все сообщения от удалённых аккаунтов
# Значение RESTORE_DELETED_ACCOUNTS_IN_* должно быть False
CLEAR_DELETED_ACCOUNTS_IN_HTML=False
"""Значение True стирает все сообщения от удалённых аккаунтов в HTML файлах"""

CLEAR_DELETED_ACCOUNTS_IN_JSON=False
"""Значение True стирает все сообщения от удалённых аккаунтов в JSON файле"""

COPY_MISSING_ASSETS=True
"""
Значение True копирует и недостающие assets (фото, видео и так далее).
Ассеты НЕ перезапишут уже существующие.
"""

COPY_MISSING_ASSETS_USE_REFLINK=True
"""Копирование ассетов при помощи REFLINK (см. `BACKUP_REFLINK_USE`)"""

GLUE_INTO_NEW_HTML=False
"""
Значение True объединяет все messages.html файлы в один огромный файл.
Примечание: это может увеличить потребление оперативной памяти.
Старые html файлы также не будут удалены
"""

GLUE_FILENAME_HTML="ALL_MESSAGES.html"
"""Название HTML файла при `GLUE_INTO_NEW_HTML=True`"""

SPLIT_HTML_FILES=False
"""
Если изменений слишком много, то может возникнуть потребность заново разделить все HTML файлы
Скрипт может сделать это двумя путями:
- `SPLIT_COUNT_HTML_FILES`
- `SPLIT_NUMBER_MESSAGES_IN_ONE_HTML_FILE`

Вы НЕ можете одновременно указать две переменные.

! Это пересоздаст ваши messages.html файлы, рекомендуем использовать `BACKUP_HTML_FILES=True`
"""

SPLIT_COUNT_HTML_FILES=0
"""Укажите количество HTML файлов, которые вы хотите получить на выходе (см. `SPLIT_HTML_FILES`)"""

SPLIT_NUMBER_MESSAGES_IN_ONE_HTML_FILE=0
"""
Укажите количество сообщений в одном HTML файле.
В зависимости от настроек, HTML файлов может стать слишком много.
См. `SPLIT_HTML_FILES`
"""