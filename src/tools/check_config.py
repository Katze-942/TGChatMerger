import config
import sys
import os
from classes.Logger import Logger
from typing import Dict, Any, Type

# Какой тип должен быть у каждой переменной
config_types: Dict[str, Type] = {
    "PARSING_JSON": bool,
    "PARSING_HTML": bool,
    # "PATH_TD_EXPORTS": list,
    "PATH_TD_EXPORTS": str,  # TODO: временная заглушка
    "PATH_LATEST_TD_EXPORT": str,
    "CONSOLE_LEVEL_DETAIL": config.LogLevel,
    "CONSOLE_COLOR": bool,
    "BACKUP_FOLDER_PATH": str,
    "BACKUP_HTML_FILES": bool,
    "BACKUP_JSON_FILE": bool,
    "BACKUP_REFLINK_USE": bool,
    "BACKUP_ARCHIVE": bool,
    "BACKUP_ARCHIVE_NAME": str,
    "BACKUP_ARCHIVE_COMPRESSION": config.CompressionType,
    "BACKUP_ARCHIVE_COMPRESS_LEVEL": int,
    "RESTORE_DELETED_ACCOUNTS_IN_HTML": bool,
    "RESTORE_DELETED_ACCOUNTS_IN_JSON": bool,
    "CLEAR_DELETED_ACCOUNTS_IN_HTML": bool,
    "CLEAR_DELETED_ACCOUNTS_IN_JSON": bool,
    "COPY_MISSING_ASSETS": bool,
    "COPY_MISSING_ASSETS_USE_REFLINK": bool,
    "GLUE_INTO_NEW_HTML": bool,
    "GLUE_FILENAME_HTML": str,
    "SPLIT_HTML_FILES": bool,
    "SPLIT_COUNT_HTML_FILES": int,
    "SPLIT_NUMBER_MESSAGES_IN_ONE_HTML_FILE": int,
}

logger_config = Logger("CONFIG")


def crash(confirmation: bool = False):
    if confirmation:
        logger_config.error("Завершение работы.")
        sys.exit(1)


def get_dict_keys() -> Dict[str, type]:
    """Список всех ключей из config. Исключаем __, классы и функции."""
    return {
        key: value
        for key, value in vars(config).items()
        if not key.startswith("__")
        and not callable(value)
        and not isinstance(value, type)
    }


def check_required_keys(config_filtered: Dict[str, Any]):
    """Если отсутствует какой-то ключ из config.py - выдаём ошибку."""
    config_keys = config_filtered.keys()
    config_types_keys = config_types.keys()

    warning_keys = config_keys - config_types_keys
    error_keys = config_types_keys - config_keys

    for key in warning_keys:
        logger_config.warn(
            f'Неизвестный ключ в config.py: "{key}={config_filtered[key]}"'
        )
        config_filtered.pop(key)

    if len(error_keys) > 0:
        logger_config.error(
            f"В config.py отсутствуют следующие ключи: {', '.join(f'"{key}"' for key in error_keys)}"
        )
        crash(True)


def check_types(config_filtered: Dict[str, type]):
    """Проверка правильности всех типов."""

    success = True
    for key, value in config_filtered.items():
        if not isinstance(value, config_types[key]):
            logger_config.error(
                f'Переменная "{key}={value}" ({type(value).__name__}) не соответствует типу "{config_types[key].__name__}"!'
            )
            success = False

    crash(not success)


def check_exists_dir(key: str, check_write_access: bool, *paths: str):
    """Выдаёт ошибку, если директорий нет, она является файлом или недоступна для записи/чтения. В случае ошибки завершает работу программы."""

    success = True
    for path in paths:
        if not os.path.exists(path):
            logger_config.error(
                f'Не удаётся найти директорию "{path}" из переменной "{key}". Проверьте, настроен ли путь относительно скрипта?'
            )
            success = False
        elif not os.path.isdir(path):
            logger_config.error(
                f'Путь "{path}" из переменной "{key}" НЕ является директорией!'
            )
            success = False
        elif not os.access(path, os.R_OK):
            logger_config.error(
                f'Путь "{path}" из переменной "{key}" недоступен для чтения!'
            )
            success = False
        elif check_write_access and not os.access(path, os.W_OK):
            logger_config.error(
                f'Путь "{path}" из переменной "{key}" недоступен для записи!'
            )
            success = False

    crash(not success)


def validate_config(config_filtered: Dict[str, type]):
    """Финальная проверка всей конфигурации. Проверяет наличие директорий, соблюдение лимитов и так далее"""
    success = True

    # Проверка PATH_TD_EXPORTS и PATH_LATEST_TD_EXPORT
    # TODO: костыль
    check_exists_dir("PATH_TD_EXPORTS", False, config_filtered["PATH_TD_EXPORTS"])
    check_exists_dir(
        "PATH_LATEST_TD_EXPORT", True, config_filtered["PATH_LATEST_TD_EXPORT"]
    )

    if config_filtered["BACKUP_HTML_FILES"] or config_filtered["BACKUP_JSON_FILE"]:
        check_exists_dir(
            "BACKUP_FOLDER_PATH", True, config_filtered["BACKUP_FOLDER_PATH"]
        )

    if not (1 <= config_filtered["BACKUP_ARCHIVE_COMPRESS_LEVEL"] <= 9):
        logger_config.error(
            'Сила сжатия ("BACKUP_ARCHIVE_COMPRESS_LEVEL") не может быть больше 9 или меньше 1'
        )
        success = False

    if (
        config_filtered["RESTORE_DELETED_ACCOUNTS_IN_HTML"]
        or config_filtered["RESTORE_DELETED_ACCOUNTS_IN_JSON"]
        and (
            config_filtered["CLEAR_DELETED_ACCOUNTS_IN_HTML"]
            or config_filtered["CLEAR_DELETED_ACCOUNTS_IN_JSON"]
        )
    ):
        logger_config.error(
            "Вы не можете указать True одновременно для RESTORE_DELETED_ACCOUNTS_IN_HTML/RESTORE_DELETED_ACCOUNTS_IN_JSON и для CLEAR_DELETED_ACCOUNTS_IN_HTML/CLEAR_DELETED_ACCOUNTS_IN_JSON"
        )
        success = False

    if (
        config_filtered["SPLIT_HTML_FILES"]
        and config_filtered["SPLIT_COUNT_HTML_FILES"] <= 0
        and config_filtered["SPLIT_NUMBER_MESSAGES_IN_ONE_HTML_FILE"] <= 0
    ):
        logger_config.error(
            'Вы включили "SPLIT_HTML_FILES", однако не указали параметр "SPLIT_COUNT_HTML_FILES" или "SPLIT_NUMBER_MESSAGES_IN_ONE_HTML_FILE"'
        )
        success = False

    if (
        config_filtered["SPLIT_HTML_FILES"]
        and config_filtered["SPLIT_COUNT_HTML_FILES"] > 0
        and config_filtered["SPLIT_NUMBER_MESSAGES_IN_ONE_HTML_FILE"] > 0
    ):
        logger_config.error(
            'Вы включили "SPLIT_HTML_FILES" и указали сразу два параметра ("SPLIT_COUNT_HTML_FILES" и "SPLIT_NUMBER_MESSAGES_IN_ONE_HTML_FILE"). Укажите только один параметр.'
        )
        success = False

    crash(not success)


def start():
    logger_config.info(3, "Проверка config.py...")
    config_filtered = get_dict_keys()
    check_required_keys(config_filtered)
    check_types(config_filtered)
    validate_config(config_filtered)
    logger_config.ok(3, "Проверка завершена! Ошибок не обнаружено.")
