import os
import json
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from config import ORGANIZED_DIR
from utils.classifier import add_training_example

console = Console()

def review_pending():
    pending_items = []
    for folder in os.listdir(ORGANIZED_DIR):
        folder_path = os.path.join(ORGANIZED_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                filepath = os.path.join(folder_path, filename)
                with open(filepath, encoding='utf-8') as f:
                    items = json.load(f)
                    for idx, item in enumerate(items):
                        if item.get("review_status") == "pending" or item.get("confidence", 1.0) < 0.8:
                            pending_items.append((folder, filename, idx, item))

    if not pending_items:
        console.print("[green]✅ No pending items for review. All data is clean![/green]")
        return

    console.print(f"[yellow]📝 Found {len(pending_items)} items pending review. Starting interactive review...[/yellow]")
    
    for folder, filename, idx, item in pending_items:
        console.clear()
        console.print(f"[bold cyan]Review Item[/bold cyan] (from {folder}/{filename})")
        console.print(f"URL: [green]{item['full_url']}[/green]")
        console.print(f"Current type: [yellow]{item['type']}[/yellow] (confidence: {item.get('confidence', 1.0)}, method: {item.get('method', 'unknown')})")
        console.print(f"Tool: {item['tool']} | Date: {item.get('timestamp_str', 'N/A')}")
        new_type = Prompt.ask("Enter new type", choices=["admin", "param", "keys", "cookies", "headers", "vuln", "other"], default=item['type'])
        if new_type != item['type']:
            item['type'] = new_type
            item['review_status'] = "approved"
            item['confidence'] = 1.0
            # إضافة المثال إلى قاعدة البيانات للتدريب
            add_training_example(item['full_url'], new_type, source="user_review")
            # إعادة حفظ الملف
            filepath = os.path.join(ORGANIZED_DIR, folder, filename)
            with open(filepath, encoding='utf-8') as f:
                all_items = json.load(f)
            all_items[idx] = item
            with open(filepath, "w", encoding='utf-8') as f:
                json.dump(all_items, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✅ Updated type to {new_type}[/green]")
        else:
            item['review_status'] = "approved"
            filepath = os.path.join(ORGANIZED_DIR, folder, filename)
            with open(filepath, encoding='utf-8') as f:
                all_items = json.load(f)
            all_items[idx] = item
            with open(filepath, "w", encoding='utf-8') as f:
                json.dump(all_items, f, indent=2, ensure_ascii=False)
            console.print("[green]✅ Marked as approved (no change)[/green]")
        input("Press Enter to continue...")

    console.print("[bold green]🎉 Review completed! All pending items have been processed.[/bold green]")