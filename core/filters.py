import json
import re
import os
from config import ORGANIZED_DIR

def filter_results(type_filter=None, tool=None, regex=None, show=50):
    if not os.path.exists(ORGANIZED_DIR):
        print("❌ No organized data found. Run watcher first.")
        return

    results = []
    for folder in os.listdir(ORGANIZED_DIR):
        folder_path = os.path.join(ORGANIZED_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        tool_name = folder.split('_')[0]
        for filename in os.listdir(folder_path):
            if not filename.endswith(".json"):
                continue
            typ = filename.replace(".json", "")
            if type_filter and typ != type_filter:
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
            except Exception as e:
                print(f"⚠️ Could not read {filepath}: {e}")

    for i, item in enumerate(results[:show]):
        print(f"{i+1}. {item['full_url']} (tool: {item['tool']}, type: {item['type']}, date: {item.get('timestamp_str','N/A')})")

    print(f"\n📊 Total matching: {len(results)}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Filter parsed results")
    parser.add_argument("--type", help="Filter by type (admin, param, keys, ...)")
    parser.add_argument("--tool", help="Filter by tool name")
    parser.add_argument("--regex", help="Regex pattern to match in URL")
    parser.add_argument("--show", type=int, default=50, help="Number of results to show")
    args = parser.parse_args()
    filter_results(type_filter=args.type, tool=args.tool, regex=args.regex, show=args.show)