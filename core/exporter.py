import os
import json
import csv
import re
from config import ORGANIZED_DIR, EXPORTS_DIR

def export_results(export_type=None, tool=None, regex=None, output_format="txt", output_file=None):
    """تصدير البيانات حسب الفلاتر."""
    if not os.path.exists(ORGANIZED_DIR):
        print("❌ No organized data found.")
        return
    
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    
    # جمع البيانات
    results = []
    for folder in os.listdir(ORGANIZED_DIR):
        folder_path = os.path.join(ORGANIZED_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        tool_name = folder.split('_')[0] if '_' in folder else folder
        for filename in os.listdir(folder_path):
            if not filename.endswith(".json"):
                continue
            typ = filename.replace(".json", "")
            if export_type and typ != export_type:
                continue
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, encoding='utf-8') as f:
                    items = json.load(f)
                    for item in items:
                        if tool and item.get("tool") != tool:
                            continue
                        if regex and not re.search(regex, item.get("full_url", ""), re.IGNORECASE):
                            continue
                        results.append(item)
            except:
                pass
    
    if not results:
        print("❌ No results match the filters.")
        return
    
    # تحديد اسم الملف إذا لم يتم توفيره
    if not output_file:
        parts = []
        if export_type:
            parts.append(export_type)
        if tool:
            parts.append(tool)
        if regex:
            parts.append("regex")
        if not parts:
            parts.append("all")
        output_file = f"export_{'_'.join(parts)}.{output_format}"
    
    output_path = os.path.join(EXPORTS_DIR, output_file)
    
    # التصدير حسب الصيغة
    if output_format == "txt":
        with open(output_path, "w", encoding='utf-8') as f:
            for item in results:
                f.write(item.get("full_url", "") + "\n")
    elif output_format == "csv":
        with open(output_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["full_url", "type", "tool", "timestamp_str", "source_file"])
            writer.writeheader()
            for item in results:
                writer.writerow({k: item.get(k, "") for k in writer.fieldnames})
    elif output_format == "json":
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    elif output_format == "burp":
        with open(output_path, "w", encoding='utf-8') as f:
            for item in results:
                f.write(item.get("full_url", "") + "\n")
    else:
        print(f"⚠️ Unsupported format: {output_format}")
        return
    
    print(f"✅ Exported {len(results)} items to {output_path}")