import os
import json
from config import ORGANIZED_DIR

OUT_DIR = os.path.join(os.path.dirname(ORGANIZED_DIR), "merged")

def merge_by_type():
    os.makedirs(OUT_DIR, exist_ok=True)
    merged = {}
    for folder in os.listdir(ORGANIZED_DIR):
        folder_path = os.path.join(ORGANIZED_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        for filename in os.listdir(folder_path):
            if not filename.endswith(".json"):
                continue
            typ = filename.replace(".json", "")
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, encoding='utf-8') as f:
                    items = json.load(f)
                    merged.setdefault(typ, []).extend(items)
            except Exception as e:
                print(f"⚠️ Could not read {filepath}: {e}")

    for typ, items in merged.items():
        out_path = os.path.join(OUT_DIR, f"{typ}.json")
        with open(out_path, "w", encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        print(f"✅ Merged {len(items)} items into {out_path}")

if __name__ == "__main__":
    merge_by_type()