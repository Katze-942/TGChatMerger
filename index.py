import config
from pathlib import Path
import json
import os
import shutil

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
    [msg["id"] for msg in new_messages]  # Запоминаем добавленные ID

    # Копируем файлы для новых сообщений с переименованием при необходимости
    process_files_with_rename(new_messages, source_folder, dest_folder)

    # Объединяем массивы, сортируя их по ID
    merged_messages = sorted(messages2 + new_messages, key=lambda msg: msg["id"])

    # Сохраняем обновленный JSON
    data2["messages"] = merged_messages
    save_json(output_path, data2)
    print(f"Файл обновлен. Добавлено {len(new_messages)} сообщений. Сохранено в {output_path}")

# Выполнение
merge_and_process_json(f"{config.PATH_TD_EXPORTS}/result.json", f"{config.PATH_LATEST_TD_EXPORT}/result.json", "output.json", config.PATH_TD_EXPORTS, config.PATH_LATEST_TD_EXPORT)
