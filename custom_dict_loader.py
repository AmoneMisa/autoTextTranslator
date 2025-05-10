import xml.etree.ElementTree as ET
import os

def load_custom_dict(xml_path):
    if not os.path.exists(xml_path):
        return {}

    tree = ET.parse(xml_path)
    root = tree.getroot()
    result = {}

    for entry in root.findall(".//ESP"):
        orig = entry.findtext("ORIGINAL")
        trans = entry.findtext("TRADUIT")
        if orig and trans:
            result[orig.strip()] = trans.strip()
    return result

def append_to_auto_dict(xml_path, original, translated):
    if not os.path.exists(xml_path):
        root = ET.Element("DocumentElement")
        tree = ET.ElementTree(root)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Проверка на дубли
    for entry in root.findall("ESP"):
        if (entry.findtext("ORIGINAL") or "").strip() == original.strip():
            return  # Уже есть

    esp = ET.SubElement(root, "ESP")
    ET.SubElement(esp, "GRUP").text = "AUTO"
    ET.SubElement(esp, "ID").text = "00000000"
    ET.SubElement(esp, "EDID").text = ""
    ET.SubElement(esp, "CHAMP").text = "FULL"
    ET.SubElement(esp, "ORIGINAL").text = original
    ET.SubElement(esp, "TRADUIT").text = translated
    ET.SubElement(esp, "PERSO").text = ""
    ET.SubElement(esp, "INDEX").text = "1"
    ET.SubElement(esp, "STATUS").text = "0"
    ET.SubElement(esp, "IDSTEXTE").text = "-1"
    ET.SubElement(esp, "COMMENTAIRE").text = ""
    ET.SubElement(esp, "ICON").text = "-1"

    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
