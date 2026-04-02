import os
import json
import re
import time
from datetime import datetime
from utils.dashboard import register_tool, register_processed_file
from config import ORGANIZED_DIR

PATTERNS = {
    "admin": re.compile(r'https?://[^/]+/(admin|login|dashboard|wp-admin|administrator|manage)', re.IGNORECASE),
    "param": re.compile(r'.*\?.*=.*'),
    "keys": re.compile(r'(?i)(api[_-]?key|secret|token|apikey|access_token|private_key)'),
    "cookies": re.compile(r'(?i)(cookie|set-cookie)'),
    "headers": re.compile(r'(?i)(x-|header|content-type|authorization)'),
    "vuln": re.compile(r'(?i)(vuln|exploit|cve-|xss|sql|injection)'),
}

def detect_tool(filepath):
    base = os.path.basename(filepath)
    name, _ = os.path.splitext(base)
    parts = re.split(r'[-_.]', name)
    tool = parts[0].lower() if parts else "unknown"
    return tool

def detect_type(line):
    line_lower = line.lower()
    for typ, pattern in PATTERNS.items():
        if pattern.search(line):
            return typ
    return "other"

def auto_detect_and_parse(filepath):
    os.makedirs(ORGANIZED_DIR, exist_ok=True)
    tool_name = detect_tool(filepath)
    register_tool(tool_name)

    today_str = datetime.now().strftime("%Y-%m-%d")
    tool_dir = os.path.join(ORGANIZED_DIR, f"{tool_name}_{today_str}")
    os.makedirs(tool_dir, exist_ok=True)

    ext = os.path.splitext(filepath)[1].lower()
    data_by_type = {}

    now = time.time()
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source_filename = os.path.basename(filepath)

    try:
        if ext == ".json":
            with open(filepath, encoding='utf-8') as f:
                items = json.load(f)
            for item in items:
                url = None
                if isinstance(item, str):
                    url = item
                elif isinstance(item, dict):
                    url = item.get("url") or item.get("full_url") or item.get("target") or item.get("host")
                if url:
                    typ = detect_type(url)
                    data_by_type.setdefault(typ, []).append({
                        "full_url": url,
                        "type": typ,
                        "tool": tool_name,
                        "timestamp": now,
                        "timestamp_str": timestamp_str,
                        "source_file": source_filename
                    })
        else:
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                lines = f.read().splitlines()
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    typ = detect_type(line)
                    data_by_type.setdefault(typ, []).append({
                        "full_url": line,
                        "type": typ,
                        "tool": tool_name,
                        "timestamp": now,
                        "timestamp_str": timestamp_str,
                        "source_file": source_filename
                    })

        for typ, items in data_by_type.items():
            if items:
                out_path = os.path.join(tool_dir, f"{typ}.json")
                existing = []
                if os.path.exists(out_path):
                    with open(out_path, encoding='utf-8') as f:
                        existing = json.load(f)
                existing.extend(items)
                with open(out_path, "w", encoding='utf-8') as f:
                    json.dump(existing, f, indent=2, ensure_ascii=False)

        register_processed_file(filepath)
        total_items = sum(len(v) for v in data_by_type.values())
        print(f"✅ Parsed {filepath} from tool {tool_name} -> {total_items} items (saved in {tool_dir})")

    except Exception as e:
        print(f"❌ Failed parsing {filepath}: {e}")