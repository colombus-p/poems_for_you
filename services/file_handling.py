import logging
import os

logger = logging.getLogger(__name__)


# Функция, возвращающая строку с текстом страницы и её размер
def _get_part_text(text: str, start: int, page_size: int) -> tuple[str, int]:
    end_signs = "❤"     #",.!:;?"
    max_end = min(len(text), start + page_size)
    chunk = text[start:max_end]

    last_good = -1
    i = 0
    while i < len(chunk):
        if chunk[i] in end_signs:
            while i + 1 < len(chunk) and chunk[i + 1] in end_signs:
                i += 1
            seq_end = i

            after_seq = start + seq_end + 1
            if (
                after_seq == len(text)
                or text[after_seq].isspace()
                or text[after_seq].isalpha()
            ):
                last_good = seq_end
        i += 1

    if last_good != -1:
        page_text = chunk[: last_good + 1]
    else:
        page_text = chunk

    return page_text, len(page_text)


# Функция, формирующая словарь книги
def prepare_book(path: str, page_size: int = 1050) -> dict[int, str]:
    """
    Читает книгу из файла и разбивает её на страницы, заканчивающиеся на знак ❤.

    Args:
        path (str): Путь к файлу с текстом книги
        page_size (int, optional): Максимальное количество символов на странице. По умолчанию 500.

    Returns:
        dict[int, str]: Словарь, где ключи - номера страниц, значения - тексты страниц

    Raises:
        FileNotFoundError: Если файл не найден
        UnicodeDecodeError: Если возникли проблемы с кодировкой файла
    """
    try:
        with open(os.path.normpath(path), 'r', encoding='utf-8') as file:
            text = file.read()
    except Exception as e:
        logger.error("Error reading a book: %s", e)
        raise e

    book = {}
    start = 0
    page_number = 1

    while start < len(text):
        # Находим ближайший ❤ после start в пределах page_size
        end = start + page_size
        heart_pos = text.find('❤', start, min(end, len(text)))

        if heart_pos != -1:
            # Нашли ❤ - берем текст до него включительно
            page_text = text[start:heart_pos + 1]
            actual_size = len(page_text)
        else:
            # ❤ не найден - берем максимально возможный кусок
            page_text = text[start:end]
            actual_size = len(page_text)

            # Ищем последний ❤ в этом куске (если есть)
            last_heart = page_text.rfind('❤')
            if last_heart != -1:
                page_text = page_text[:last_heart + 1]
                actual_size = len(page_text)

        book[page_number] = page_text.strip()
        start += actual_size
        page_number += 1

    return book