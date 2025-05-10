from translator import LocalTranslator

if __name__ == "__main__":
    translator = LocalTranslator()
    print("🔤 Локальный переводчик NLLB (en → ru). Введите 'exit' для выхода.\n")

    while True:
        text = input("⤷ Введите текст: ").strip()
        if text.lower() == "exit":
            break
        if not text:
            continue

        translation = translator.translate(text)
        print(f"🔁 Перевод: {translation}\n")
