import os
import json
import re
from config import ORGANIZED_DIR, BURP_DIR

def generate_burp_files():
    """إنشاء ملفات Burp Suite من البيانات الموجودة في organized."""
    if not os.path.exists(ORGANIZED_DIR):
        return
    os.makedirs(BURP_DIR, exist_ok=True)
    
    # تجميع البيانات من جميع المجلدات
    all_items = []
    for folder in os.listdir(ORGANIZED_DIR):
        folder_path = os.path.join(ORGANIZED_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                filepath = os.path.join(folder_path, filename)
                try:
                    with open(filepath, encoding='utf-8') as f:
                        items = json.load(f)
                        all_items.extend(items)
                except:
                    pass
    
    if not all_items:
        return
    
    # تصنيف البيانات
    targets = set()
    admin = []
    params = []
    keys = []
    cookies = []
    headers = []
    vulns = []
    others = []
    
    for item in all_items:
        url = item.get("full_url", "")
        typ = item.get("type", "other")
        if not url:
            continue
        # استخراج النطاق الأساسي
        match = re.search(r'https?://([^/]+)', url)
        if match:
            targets.add(match.group(1))
        # التصنيف حسب النوع
        if typ == "admin":
            admin.append(url)
        elif typ == "param":
            params.append(url)
        elif typ == "keys":
            keys.append(url)
        elif typ == "cookies":
            cookies.append(url)
        elif typ == "headers":
            headers.append(url)
        elif typ == "vuln":
            vulns.append(url)
        else:
            others.append(url)
    
    # كتابة الملفات
    with open(os.path.join(BURP_DIR, "all_targets.txt"), "w", encoding='utf-8') as f:
        f.write("\n".join(sorted(targets)))
    
    with open(os.path.join(BURP_DIR, "admin_endpoints.txt"), "w", encoding='utf-8') as f:
        f.write("\n".join(admin))
    
    with open(os.path.join(BURP_DIR, "param_endpoints.txt"), "w", encoding='utf-8') as f:
        f.write("\n".join(params))
    
    with open(os.path.join(BURP_DIR, "keys.txt"), "w", encoding='utf-8') as f:
        f.write("\n".join(keys))
    
    with open(os.path.join(BURP_DIR, "cookies.txt"), "w", encoding='utf-8') as f:
        f.write("\n".join(cookies))
    
    with open(os.path.join(BURP_DIR, "headers.txt"), "w", encoding='utf-8') as f:
        f.write("\n".join(headers))
    
    with open(os.path.join(BURP_DIR, "vuln_urls.txt"), "w", encoding='utf-8') as f:
        f.write("\n".join(vulns))
    
    with open(os.path.join(BURP_DIR, "others.txt"), "w", encoding='utf-8') as f:
        f.write("\n".join(others))
    
    # صيغة Burp Target scope (تنسيق regex تقريبي)
    with open(os.path.join(BURP_DIR, "burp_targets.txt"), "w", encoding='utf-8') as f:
        for target in sorted(targets):
            f.write(f".*{re.escape(target)}.*\n")
    
    # اختياري: إحصاء سريع
    total = len(admin)+len(params)+len(keys)+len(cookies)+len(headers)+len(vulns)+len(others)
    print(f"✅ Burp files updated: {total} total items, {len(targets)} unique targets")