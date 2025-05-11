import xml.etree.ElementTree as ET
import os

def load_custom_dict(xml_path):
    import os
    import xml.etree.ElementTree as ET

    if not os.path.exists(xml_path):
        print(f"❌ Файл {xml_path} не найден.")
        return {}

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        result = {}

        # Поддержка как ESP, так и BDD
        for entry in root.findall(".//BDD") + root.findall(".//ESP"):
            orig = entry.findtext("ORIGINAL")
            trans = entry.findtext("TRADUIT")
            if orig and trans:
                result[orig.strip()] = trans.strip()

        print(f"✅ Загружено {len(result)} записей из {xml_path}")
        return result
    except Exception as e:
        print(f"❌ Ошибка при загрузке словаря: {e}")
        return {}

def append_to_auto_dict(xml_path, original, translated):
    if not os.path.exists(xml_path):
        root = ET.Element("DocumentElement")
        tree = ET.ElementTree(root)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Проверка на дубликаты
    for entry in root.findall("BDD"):
        if (entry.findtext("ORIGINAL") or "").strip() == original.strip():
            return  # Уже есть — не добавляем

    bdd = ET.SubElement(root, "BDD")
    ET.SubElement(bdd, "GRUP").text = "AUTO"
    ET.SubElement(bdd, "ID").text = "00000000"
    ET.SubElement(bdd, "EDID").text = ""
    ET.SubElement(bdd, "CHAMP").text = "FULL"
    ET.SubElement(bdd, "ORIGINAL").text = original
    ET.SubElement(bdd, "TRADUIT").text = translated
    ET.SubElement(bdd, "PERSO")
    ET.SubElement(bdd, "INDEX").text = "0"

    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    print(f"📥 Добавлено в авто-словарь: {original} → {translated}")