import subprocess
from pathlib import Path
import re
from random import randint, choice
from typing import List

SCRIPT_NAME = "task.py"  # имя файла для временного скрипта
TEMPLATE_NAME = "temp1.txt"  # имя файла с шаблоном
OUTPUT_FILE_NAME = "gift_q.txt"  # имя файла со списком вопросов
IS_FINITE = False  # нужно ли определённо количество вариантов
MAX_Q_COUNT = 5  # количество вопросов


def get_result(source_code: str) -> str:

    with open(SCRIPT_NAME, "w", encoding="utf-8") as task_source_code:
        task_source_code.write(source_code)

    # Python 3.4-3.7
    output = subprocess.run(
        ["python", str(Path().absolute() / SCRIPT_NAME)],
        stdout=subprocess.PIPE,
        timeout=10,
        encoding="utf-8",
    )
    try:
        Path(SCRIPT_NAME).unlink()
    except FileNotFoundError:
        pass
    return output.stdout


def get_random_code(lines: List[str]) -> str:
    # поиск разметки с диапазонами и замена на случайные значения
    range_pipe = []
    for line in lines:
        current_line = line
        for start, finish in re.findall("{{(-?[0-9]+)\.\.(-?[0-9]+)}}", current_line):
            rand_num = randint(int(start), int(finish))
            current_line = current_line.replace(
                f"{{{{{start}..{finish}}}}}", str(rand_num), 1
            )
        range_pipe.append(current_line)

    full_source_code = "".join(range_pipe)
    # поиск разметки с вариантами на выбор
    # флаг S нужен для поиска по
    for options_str, _ in re.findall(
        "\\[\\[((.+?#)+?.+?)\\]\\]", full_source_code, flags=re.S
    ):
        # выбор одного из вариантов
        selected_option = choice(options_str.split("#"))
        # меняем список вариантов на выбранный вариант
        full_source_code = full_source_code.replace(
            f"[[{options_str}]]", selected_option, 1
        )

    # выбираем случайные имена для переменных
    for names_str, _ in re.findall(
        "{{(([a-zA-Z0-9_-]+=)+[a-zA-Z0-9_-]+)}}", full_source_code
    ):
        options_list = names_str.split("=")
        selected_option = choice(options_list)

        full_source_code = full_source_code.replace(
            f"{{{{{names_str}}}}}", selected_option
        )

        for option in options_list:
            full_source_code = full_source_code.replace(
                f"{{{{{option}}}}}", selected_option
            )

    return full_source_code


def create_questing_text(src: str, result: str) -> str:
    # добавляем неразрывный пробел Alt+0160
    # без него не появятся отступы в коде
    full_source_code = src.replace("  ", "\xa0 ")
    return f"[markdown]Запишите результат выполнения следующей программы:\n```\n{full_source_code.strip()}\n```\n{{={result.rstrip()}}}\n\n\n"


# чтение шаблона
source = ""
with open(TEMPLATE_NAME, "r", encoding="utf-8") as template:
    source = template.readlines()  # чтение шаблона по строкам

print("[*] Текущий шаблон:")
print("".join(source))


random_timeout = 0  # количество попыток сгенерировать исходный код
unique_codes = set()  # хранение уникальных сгенерированных исходных кодов

with open(OUTPUT_FILE_NAME, "w", encoding="utf-8") as gift_file:

    while True:

        full_source_code = get_random_code(source)

        while full_source_code in unique_codes and random_timeout < 20:
            full_source_code = get_random_code(source)
            random_timeout += 1

        if random_timeout > 19:
            break

        random_timeout = 0
        unique_codes.add(full_source_code)

        print("[*] Новый вопрос")
        print(full_source_code)

        try:
            result = get_result(full_source_code)
            q = create_questing_text(full_source_code, result)
            gift_file.write(q)
        except subprocess.TimeoutExpired:
            print("[!] Время выполнения вышло")
        except Exception as e:
            print("[!] Ошибка при запуске программы. Пропускаем")
            print(e)

        MAX_Q_COUNT -= 1
        if IS_FINITE and MAX_Q_COUNT == 0:
            break

print(f"[*] Вопросы готовы. Количество - {len(unique_codes)}")
