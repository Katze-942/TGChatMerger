import json
import os
import shutil
from pathlib import Path
from datetime import date
from datetime import time

### === Основные параметры === ###
# Будет сравниваться JSON и HTML файл при их наличии
PARSING_JSON=True
PARSING_HTML=True

# Укажите путь до старых папок с экспортом Telegram чата.
# Путь должен быть относительно того места, откуда запускается скрипт
PATH_OLD_TD_EXPORTS=["ChatExport 2025-01-29-old"][0] # TODO: [0] является заглушкой

# Укажите путь до последнего экспорта Telegram чата. В этой директории будут изменяться файлы.
# Путь должен быть относительно того места, откуда запускается скрипт
PATH_LATEST_TD_EXPORT="ChatExport 2025-01-29-new"

### === Резервное копирование === ###
# Путь, в котором будет сделана резервная копия HTML и JSON файлов
BACKUP_FOLDER_PATH=f"{PATH_LATEST_TD_EXPORT}/Backup"

# Резервная копия HTML файлов
BACKUP_HTML_FILES=True

# Резервная копия JSON файла
BACKUP_JSON_FILE=True

# Полезно, если у вас файловая система btrfs или другая CoW файловая система
# Для работы необходимо установить модуль reflink (https://reflink.readthedocs.io):
# pip install reflink
BACKUP_REFLINK_USE=True

# По умолчанию создаётся резервная копия путём обычного копирования.
# Установите True, если хотите сжать бэкап в один ZIP архив: 
BACKUP_ARCHIVE=False

# Название архива. По умолчанию: дата время.zip
BACKUP_ARCHIVE_NAME=f"{date.today()} {time()}.zip"

# Тип сжатия. Поддерживается: ZIP_STORED (без сжатия), ZIP_DEFLATED (стандартное сжатие), ZIP_BZIP2 (сжатие через bzip2), ZIP_LZMA (сжатие через lzma)
BACKUP_ARCHIVE_COMPRESSION="ZIP_LZMA"

# Сила сжатия от 1 до 9
BACKUP_ARCHIVE_COMPRESS_LEVEL=9

### === ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ === ###
# В вашем Telegram экспорте могут быть сообщения от удалённых аккаунтов
# Если скрипт найдёт имя аккаунта в старых экспортах, то его имя можно будет восстановить
# Установите True, если хотите, чтобы программа восстановила названия аккаунтов
RESTORE_DELETED_ACCOUNTS_IN_HTML=False
RESTORE_DELETED_ACCOUNTS_IN_JSON=False

# Противоположность предыдущего параметра. При True убирает все сообщения от удалённых аккаунтов
# Значение RESTORE_DELETED_ACCOUNTS_IN_* должно быть False
CLEAR_DELETED_ACCOUNTS_IN_HTML=False
CLEAR_DELETED_ACCOUNTS_IN_JSON=False

# Скрипт помимо сообщений может копировать и недостающие assets (фото, видео и так далее)
# Ассеты НЕ перезапишут уже существующие.
COPY_MISSING_ASSETS=True
COPY_MISSING_ASSETS_USE_REFLINK=True # Тоже самое, что и BACKUP_REFLINK_USE.

# Установите значение True, если хотите чтобы все messages.html были объединены в один огромный файл
# Примечание: это может увеличить потребление оперативной памяти. Старые html файлы также не будут удалены
GLUE_INTO_NEW_HTML_=False
GLUE_FILENAME_HTML="ALL_MESSAGES.html"

# Если изменений слишком много, то может возникнуть потребность заново разделить все HTML файлы
# Скрипт может сделать это двумя путями:
# 1. Укажите SPLIT_COUNT_HTML_FILES. Скрипт разделит сообщения ровно на то количество файлов, которые вы укажете в переменной
# 2. Укажите SPLIT_NUMBER_MESSAGES_IN_ONE_HTML_FILE. Тогда в одном HTML будет ровно столько-то сообщений. В зависимости от настроек их может стать слишком много. 
# Вы НЕ можете одновременно указать две переменные.
# ! Это пересоздаст ваши messages.html файлы, рекомендуем использовать BACKUP_HTML_FILES=True
SPLIT_HTML_FILES=False
SPLIT_COUNT_HTML_FILES=0
SPLIT_NUMBER_MESSAGES_IN_ONE_HTML_FILE=0



# Путь к файлам
# file1_path = "result-old.json"  # Исходный JSON 1
# file2_path = "result-new.json"  # Исходный JSON 2
# output_path = "output.json"  # Итоговый JSON
# source_folder = "ChatExport_2024-05-27"  # Папка с исходными файлами
# dest_folder = "ChatExport_2024-05-27-latest"  # Целевая папка для копирования

# Чтение JSON-файлов
def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
        data = json.loads(content)
        return data, content

# Запись JSON
def save_json(filepath, data):
    formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(formatted_data)

# Копирование файла с переименованием при конфликте
def copy_file_with_rename(source, destination):
    # Если файл существует, переименуем
    destination_path = Path(destination)
    if destination_path.exists():
        base = destination_path.stem
        ext = destination_path.suffix
        parent = destination_path.parent
        counter = 1

        # Поиск уникального имени
        while destination_path.exists():
            destination_path = parent / f"{base}_{counter}{ext}"
            counter += 1

    # Копируем файл
    os.makedirs(destination_path.parent, exist_ok=True)
    shutil.copy2(source, destination_path)
    return str(destination_path)

# Обработка параметров file и thumbnail с переименованием
def process_files_with_rename(messages, source_folder, dest_folder):
    for msg in messages:
        for key in ['file', 'thumbnail']:
            if key in msg and msg[key]:
                source_path = os.path.join(source_folder, msg[key])
                dest_path = os.path.join(dest_folder, msg[key])
                try:
                    # Копируем с переименованием в случае конфликта
                    new_path = copy_file_with_rename(source_path, dest_path)
                    msg[key] = os.path.relpath(new_path, dest_folder)  # Обновляем путь в JSON
                    print(f"Скопирован файл: {source_path} -> {new_path}")
                except FileNotFoundError:
                    print(f"Ошибка: Файл {source_path} не найден и пропущен.")
                except Exception as e:
                    print(f"Ошибка при копировании {source_path}: {e}")

# Основная логика
def merge_and_process_json(file1_path, file2_path, output_path, source_folder, dest_folder):
    # Загружаем JSON-файлы
    data1, _ = load_json(file1_path)
    data2, _ = load_json(file2_path)

    # Извлекаем массивы сообщений
    messages1 = data1["messages"]
    messages2 = data2["messages"]

    # Создаем множество ID из второго массива
    ids_in_file2 = {msg["id"] for msg in messages2}

    # Находим новые сообщения
    new_messages = [msg for msg in messages1 if msg["id"] not in ids_in_file2]
    array_id = [msg["id"] for msg in new_messages]  # Запоминаем добавленные ID

    # Копируем файлы для новых сообщений с переименованием при необходимости
    process_files_with_rename(new_messages, source_folder, dest_folder)

    # Объединяем массивы, сортируя их по ID
    merged_messages = sorted(messages2 + new_messages, key=lambda msg: msg["id"])

    # Сохраняем обновленный JSON
    data2["messages"] = merged_messages
    save_json(output_path, data2)
    print(f"Файл обновлен. Добавлено {len(new_messages)} сообщений. Сохранено в {output_path}")

# Выполнение
merge_and_process_json(f"{PATH_OLD_TD_EXPORTS}/result.json", f"{PATH_LATEST_TD_EXPORT}/result.json", "output.json", PATH_OLD_TD_EXPORTS, PATH_LATEST_TD_EXPORT)
