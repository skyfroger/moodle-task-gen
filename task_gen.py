import subprocess
from pathlib import Path
import re
from random import randint, choice
from typing import List

def get_result():
    # Python 3.4-3.7
    subprocess.run([Path().absolute() / "abc" / "pabcnetcclear.exe", "task.pas"],
                   stdout=subprocess.PIPE, timeout=30)
    output = subprocess.run([Path().absolute() / "task.exe"], stdout=subprocess.PIPE,
                            timeout=5, encoding="utf-8")
    try:
        Path("task.exe").unlink()
    except FileNotFoundError:
        pass
    return output.stdout


def get_random_code(lines: List[str])->str:
    # поиск разметки с диапазонами и замена на случайные значения
    range_pipe = []
    for line in lines:
        current_line = line
        for start, finish in re.findall("{{(-?[0-9]+)\.\.(-?[0-9]+)}}", current_line):
            rand_num = randint(int(start), int(finish))
            current_line= current_line.replace(f"{{{{{start}..{finish}}}}}", str(rand_num), 1)
        range_pipe.append(current_line)
            
    full_source_code = "".join(range_pipe)
    # поиск разметки с вариантами на выбор
    # флаг S нужен для поиска по 
    for options_str, _ in re.findall("\\[\\[((.+?#)+?.+?)\\]\\]",full_source_code, flags=re.S):
        # выбор одного из вариантов
        selected_option = choice(options_str.split("#"))
        # меняем список вариантов на выбранный вариант
        full_source_code = full_source_code.replace(f"[[{options_str}]]", selected_option, 1)
    
    
    # выбираем случайные имена для переменных
    for names_str, _ in re.findall("{{(([a-zA-Z0-9_-]+=)+[a-zA-Z0-9_-]+)}}", full_source_code):
        options_list = names_str.split("=")
        selected_option = choice(options_list)
        
        full_source_code = full_source_code.replace(f"{{{{{names_str}}}}}", selected_option)
        
        for option in options_list:
            full_source_code = full_source_code.replace(f"{{{{{option}}}}}", selected_option)
    
    return full_source_code

def create_questing_text(src: str, result: str)->str:
    # добавляем неразрывный пробел Alt+0160
    # без него не появятся отступы в коде
    full_source_code = src.replace("  ", "\xa0 ")
    return f"[markdown]Запишите результат выполнения следующей программы:\n```\n{full_source_code.strip()}\n```\n{{={result.rstrip()}}}\n\n\n"

# чтение шаблона
source = ""
with open("шаблон1.txt", 'r', encoding="utf-8") as template:
    source = template.readlines() # чтение шаблона по строкам

print("Текущий шаблон:")
print("".join(source))

with open("gift_q.txt", 'w', encoding="utf-8") as gift_file:
    
    for i in range(1):
        full_source_code = get_random_code(source)
        print(full_source_code)
        print(f"Задача {i+1}")
        
        with open("task.pas", 'w', encoding="utf-8") as task_source_code:
            task_source_code.write(full_source_code)
        try:    
            result = get_result()
            q = create_questing_text(full_source_code, result)
            gift_file.write(q)
        except subprocess.TimeoutExpired:
            print("[!] Время выполнения вышло")
        except Exception as e:
            print("[!] Ошибка при запуске программы. Пропускаем")
            print(e)

print("Вопросы готовы")
