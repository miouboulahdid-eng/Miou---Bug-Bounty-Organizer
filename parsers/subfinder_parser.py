import json, os

def parse_file(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines()
    
    entries = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        entries.append({
            "full_url": f"https://{line}",
            "type": "param"  # مثال تصنيف ذكي
        })
    
    out_file = filepath + ".json"
    with open(out_file, "w") as f:
        json.dump(entries, f, indent=2)
    
    print(f"✅ Parsed {len(entries)} entries from {os.path.basename(filepath)}")