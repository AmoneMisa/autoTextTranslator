import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import os
import csv
import xml.etree.ElementTree as ET
from translator import LocalTranslator

translator = LocalTranslator()
EXCLUDED_KEYS = {'script', 'Script', 'SCRIPT', 'id', 'formid'}

from custom_dict_loader import load_custom_dict, append_to_auto_dict

MANUAL_DICT_PATH = "custom_translation_dict.xml"
AUTO_DICT_PATH = "auto_generated_translations.xml"

MANUAL_DICT = load_custom_dict(MANUAL_DICT_PATH)
AUTO_DICT = load_custom_dict(AUTO_DICT_PATH)

def normalize(text):
    return (
        text.strip()
        .replace('\n', '')
        .replace('\r', '')
        .replace('"', '')
        .replace('«', '')
        .replace('»', '')
        .strip()
        .lower()
    )

IGNORED_KEYS = {"default", "script", "default value"}

def translate_text(text):
    cleaned = normalize(text)

    if cleaned.lower() in IGNORED_KEYS:
        print(f"[🚫 IGNORE] '{text}' → '{text}'")
        return text

    for key, val in MANUAL_DICT.items():
        if normalize(key) == cleaned:
            print(f"[✔️ MANUAL] '{text}' == '{key}' → '{val}'")
            return val

    for key, val in AUTO_DICT.items():
        if normalize(key) == cleaned:
            print(f"[🧠 AUTO] '{text}' → '{val}'")
            return val

    translated = translator.translate(text)
    print(f"[⚠️  AI   ] '{text}' → '{translated}'")
    append_to_auto_dict(AUTO_DICT_PATH, text.strip(), translated.strip())
    return translated

def get_autosave_path(input_path):
    base, ext = os.path.splitext(input_path)
    return base + "_translated" + ext

def translate_txt(path, output_path, progress_callback):
    with open(path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    total = len(lines)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for i, line in enumerate(lines, 1):
            outfile.write(translate_text(line) + '\n')
            progress_callback(i / total * 100)

def translate_csv(path, output_path, progress_callback):
    with open(path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows = list(reader)
    total = len(rows)
    new_rows = []
    for i, row in enumerate(rows, 1):
        new_row = {}
        for key in fieldnames:
            if key.lower() in EXCLUDED_KEYS:
                new_row[key] = row[key]
            else:
                new_row[key] = translate_text(row[key])
        new_rows.append(new_row)
        progress_callback(i / total * 100)

    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_rows)

def translate_xml(path, output_path, progress_callback):
    tree = ET.parse(path)
    root = tree.getroot()
    elements = list(root.iter("ESP"))
    total = len(elements)

    for i, esp in enumerate(elements, 1):
        original = esp.find("ORIGINAL")
        traduit = esp.find("TRADUIT")

        if (
                original is not None and
                original.text and
                traduit is not None and
                not any(key in original.tag.lower() for key in ("script", "default"))
        ):
            translated_text = translate_text(original.text)
            traduit.text = translated_text

        progress_callback(i / total * 100)

    tree.write(output_path, encoding='utf-8', xml_declaration=True)

def start_translation():
    input_path = file_path.get()
    output_path = save_path.get() or get_autosave_path(input_path)

    if not input_path:
        messagebox.showwarning("Ошибка", "Укажите входной файл.")
        return

    try:
        ext = os.path.splitext(input_path)[1].lower()
        progress["value"] = 0
        root.update_idletasks()

        def update_progress(value):
            progress["value"] = value
            root.update_idletasks()

        if ext == '.txt':
            translate_txt(input_path, output_path, update_progress)
        elif ext == '.csv':
            translate_csv(input_path, output_path, update_progress)
        elif ext == '.xml':
            translate_xml(input_path, output_path, update_progress)
        else:
            messagebox.showerror("Неподдерживаемый формат", f"Формат файла {ext} не поддерживается.")
            return

        messagebox.showinfo("Готово", f"Перевод завершён. Сохранено в:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def change_theme(theme_name):
    root.style.theme_use(theme_name)

# Инициализация окна
root = ttk.Window(themename="flatly")
root.title("Локальный переводчик (en → ru)")
root.geometry("620x470")

file_path = ttk.StringVar()
save_path = ttk.StringVar()

ttk.Label(root, text="Файл для перевода (.txt / .csv / .xml):").pack(pady=(10, 0))
ttk.Entry(root, textvariable=file_path, width=70).pack()
ttk.Button(root, text="Выбрать файл", command=lambda: file_path.set(filedialog.askopenfilename())).pack(pady=5)

ttk.Label(root, text="Сохранить как (необязательно):").pack()
ttk.Entry(root, textvariable=save_path, width=70).pack()
ttk.Button(root, text="Сохранить в...", command=lambda: save_path.set(filedialog.asksaveasfilename())).pack(pady=5)

progress = ttk.Progressbar(root, length=500, mode='determinate')
progress.pack(pady=10)

ttk.Label(root, text="Перевод выполняется только с английского на русский", foreground="gray").pack()

# 🎨 Темы оформления
ttk.Label(root, text="Тема оформления:").pack(pady=(20, 0))
themes = root.style.theme_names()
theme_var = ttk.StringVar(value=root.style.theme_use())
theme_combo = ttk.Combobox(root, textvariable=theme_var, values=themes, state="readonly", width=30)
theme_combo.pack()
theme_combo.bind("<<ComboboxSelected>>", lambda e: change_theme(theme_var.get()))

ttk.Button(root, text="Перевести", bootstyle=SUCCESS, command=start_translation).pack(pady=20)

root.mainloop()
