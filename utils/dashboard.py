from rich.console import Console, Group
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from collections import deque
import os
import json
import time
import threading
import re
import shutil
import psutil
from datetime import datetime
from config import ORGANIZED_DIR, RAW_DIR, LOGS_DIR

console = Console()
CHECK_INTERVAL = 2
FALLBACK_TIMEOUT = int(os.environ.get("BBO_FALLBACK_TIMEOUT", 10))
MAX_LOG_ENTRIES = 30

DATA_TYPES = ["admin", "param", "keys", "cookies", "headers", "vuln", "other"]

EMOJI_MAP = {
    "admin": "🔐",
    "param": "🔗",
    "keys": "🗝️",
    "cookies": "🍪",
    "headers": "📡",
    "vuln": "💥",
    "other": "📄"
}

LOGO = """
[bold cyan]╔═════════════════════════════════════════════════
║                                                           ║
║     ███╗   ███╗██╗ ██████╗ ██╗   ██╗     🐺               ║
║     ████╗ ████║██║██╔═══██╗██║   ██║                      ║
║     ██╔████╔██║██║██║   ██║██║   ██║                      ║
║     ██║╚██╔╝██║██║██║   ██║██║   ██║                      ║
║     ██║ ╚═╝ ██║██║╚██████╔╝╚██████╔╝                      ║
║     ╚═╝     ╚═╝╚═╝ ╚═════╝  ╚═════╝                       ║
║     Bug Bounty Organizer - Real-time Dashboard  
╚══════════════════════════════════════════════════════════════════╝[/bold cyan]
"""

KNOWN_RECON_TOOLS = {
    "subfinder", "httpx", "nuclei", "gau", "katana", "ffuf", "gobuster",
    "amass", "naabu", "dnsx", "httprobe", "waybackurls", "unfurl",
    "qsreplace", "gf", "crlfuzz", "dalfox", "kxss", "interactsh-client"
}

active_tools = {}
active_tools_lock = threading.Lock()
start_time = time.time()
last_processed_file = {"name": None, "time": 0}
event_log = deque(maxlen=MAX_LOG_ENTRIES)
previous_running_tools = set()
last_log_mtime = 0

def read_miou_commands():
    global last_log_mtime
    log_file = os.path.join(LOGS_DIR, "miou_commands.log")
    if not os.path.exists(log_file):
        return
    mtime = os.path.getmtime(log_file)
    if mtime == last_log_mtime:
        return
    last_log_mtime = mtime
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines[-10:]:
            line = line.strip()
            if line and not any(line in entry for entry in event_log):
                event_log.append(line)
    except:
        pass

def add_log(message, style="white"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    event_log.append(log_entry)

def register_tool(tool_name):
    with active_tools_lock:
        if tool_name not in active_tools:
            add_log(f"🟢 Tool '{tool_name}' started", "green")
        active_tools[tool_name] = time.time()

def register_processed_file(filepath):
    global last_processed_file
    last_processed_file["name"] = os.path.basename(filepath)
    last_processed_file["time"] = time.time()
    add_log(f"✅ Parsed: {os.path.basename(filepath)}", "cyan")

def get_running_recon_tools():
    running = set()
    tools_from_files = set()
    try:
        for item in os.listdir(ORGANIZED_DIR):
            if os.path.isdir(os.path.join(ORGANIZED_DIR, item)):
                tool_name = item.split('_')[0]
                if len(tool_name) > 2:
                    tools_from_files.add(tool_name)
        for filename in os.listdir(RAW_DIR):
            base = filename.rsplit('.', 1)[0]
            parts = re.split(r'[-_.]', base)
            tool = parts[0].lower() if parts else "unknown"
            if len(tool) > 2:
                tools_from_files.add(tool)
    except:
        pass

    allowed_tools = KNOWN_RECON_TOOLS.union(tools_from_files)

    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name'].lower()
            base_name = name.split('.')[0] if '.' in name else name
            if base_name in allowed_tools or base_name in tools_from_files:
                running.add(base_name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return running

def update_tool_status_logs():
    global previous_running_tools
    current = get_running_recon_tools()
    new_tools = current - previous_running_tools
    stopped_tools = previous_running_tools - current
    for tool in new_tools:
        add_log(f"🟢 Process '{tool}' started", "green")
    for tool in stopped_tools:
        add_log(f"🔴 Process '{tool}' stopped", "red")
    previous_running_tools = current

def get_tool_last_activity(tool_name):
    last = 0
    with active_tools_lock:
        if tool_name in active_tools:
            last = max(last, active_tools[tool_name])
    try:
        for filename in os.listdir(RAW_DIR):
            if tool_name in filename:
                path = os.path.join(RAW_DIR, filename)
                mtime = os.path.getmtime(path)
                if mtime > last:
                    last = mtime
    except:
        pass
    try:
        for folder in os.listdir(ORGANIZED_DIR):
            if folder.startswith(tool_name + "_"):
                folder_path = os.path.join(ORGANIZED_DIR, folder)
                for f in os.listdir(folder_path):
                    if f.endswith(".json"):
                        path = os.path.join(folder_path, f)
                        mtime = os.path.getmtime(path)
                        if mtime > last:
                            last = mtime
    except:
        pass
    return last

def get_active_tools_list():
    now = time.time()
    running_tools = get_running_recon_tools()
    active_list = []

    all_tools = set()
    with active_tools_lock:
        all_tools.update(active_tools.keys())
    try:
        for filename in os.listdir(RAW_DIR):
            base = filename.rsplit('.', 1)[0]
            parts = re.split(r'[-_.]', base)
            tool = parts[0].lower() if parts else "unknown"
            if len(tool) > 2:
                all_tools.add(tool)
        for folder in os.listdir(ORGANIZED_DIR):
            if "_" in folder:
                tool_name = folder.split('_')[0]
                all_tools.add(tool_name)
    except:
        pass

    for tool in running_tools:
        all_tools.add(tool)

    for tool in all_tools:
        last_activity = get_tool_last_activity(tool)
        if tool in running_tools or (now - last_activity < FALLBACK_TIMEOUT):
            active_list.append((tool, last_activity))
    return active_list

def read_tool_data(tool_name):
    data_counts = {t: 0 for t in DATA_TYPES}
    try:
        for folder in os.listdir(ORGANIZED_DIR):
            if folder.startswith(tool_name + "_"):
                folder_path = os.path.join(ORGANIZED_DIR, folder)
                for f in os.listdir(folder_path):
                    if f.endswith(".json"):
                        typ = f.replace(".json", "")
                        if typ in DATA_TYPES:
                            with open(os.path.join(folder_path, f), encoding='utf-8') as file:
                                items = json.load(file)
                                data_counts[typ] += len(items)
    except Exception:
        pass
    return data_counts

def get_pending_files_count():
    try:
        return len(os.listdir(RAW_DIR))
    except:
        return 0

def build_tools_table(active_tools_list):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("🛠️ Tool", justify="center", style="cyan")
    table.add_column("⚡", justify="center")
    table.add_column("📦 Total", justify="right", style="green")
    for t in DATA_TYPES:
        emoji = EMOJI_MAP.get(t, "📄")
        table.add_column(f"{emoji} {t}", justify="right")

    now = time.time()
    running_set = get_running_recon_tools()

    if not active_tools_list:
        table.add_row("[bold yellow]📂 No active recon tools[/bold yellow]", "", "", "", "", "", "", "", "", "")
        table.add_row("[italic]💡 Helpful Tips:[/italic]", "", "", "", "", "", "", "", "", "")
        table.add_row("   • Place your tool output files in [cyan]'data/raw/'[/cyan] directory", "", "", "", "", "", "", "", "", "")
        table.add_row("   • Run Recon tools like [green]subfinder, httpx, nuclei, gau[/green]", "", "", "", "", "", "", "", "", "")
        table.add_row("   • Files are auto-detected, parsed and organized by tool & date", "", "", "", "", "", "", "", "", "")
        table.add_row("   • Use [yellow]--clean[/yellow] to reset old data before a new session", "", "", "", "", "", "", "", "", "")
        return table

    for tool_name, last_time in sorted(active_tools_list, key=lambda x: x[1], reverse=True):
        counts = read_tool_data(tool_name)
        total = sum(counts.values())
        if tool_name in running_set:
            status_icon = "🟢"
        else:
            status_icon = "🟡"
        table.add_row(
            tool_name,
            status_icon,
            str(total),
            str(counts.get("admin", 0)),
            str(counts.get("param", 0)),
            str(counts.get("keys", 0)),
            str(counts.get("cookies", 0)),
            str(counts.get("headers", 0)),
            str(counts.get("vuln", 0)),
            str(counts.get("other", 0))
        )
    return table

def build_stats_panel(active_tools_list):
    type_totals = {t: 0 for t in DATA_TYPES}
    total_items = 0
    for tool_name, _ in active_tools_list:
        counts = read_tool_data(tool_name)
        for typ in DATA_TYPES:
            type_totals[typ] += counts.get(typ, 0)
        total_items += sum(counts.values())
    active_count = len(active_tools_list)
    uptime = int(time.time() - start_time)
    uptime_str = f"{uptime // 3600}h {(uptime % 3600) // 60}m {uptime % 60}s"
    sorted_types = sorted(type_totals.items(), key=lambda x: x[1], reverse=True)
    top_types = ", ".join([f"{EMOJI_MAP[t]} {t}: {v}" for t, v in sorted_types[:3] if v > 0])
    if not top_types:
        top_types = "None (no data yet)"
    
    pending = get_pending_files_count()
    last_file = last_processed_file["name"]
    last_time = last_processed_file["time"]
    last_str = "None"
    if last_file and last_time > 0:
        sec_ago = int(time.time() - last_time)
        last_str = f"{last_file} ({sec_ago}s ago)"
    
    stats_text = (
        f"[bold]⏱️ Uptime:[/] {uptime_str}    "
        f"[bold]🔧 Active Tools:[/] {active_count}\n"
        f"[bold]📊 Total Items:[/] {total_items}\n"
        f"[bold]🔥 Top Types:[/] {top_types}\n"
        f"[bold]📄 Last processed:[/] {last_str}\n"
        f"[bold]⏳ Files in raw:[/] {pending}"
    )
    return Panel(stats_text, title="📈 Live Statistics (Active Tools Only)", border_style="green")

def build_logs_panel():
    read_miou_commands()
    logs_to_show = list(event_log)[::-1]
    if not logs_to_show:
        logs_text = "[dim]No Miou commands yet. Use 'Miou start', 'Miou export', etc.[/dim]"
    else:
        logs_text = "\n".join(logs_to_show)
    return Panel(logs_text, title="📋 Miou Command History", border_style="yellow", height=12)

def build_quick_actions_panel():
    """لوحة الأوامر السريعة (Quick Actions) باستخدام جدول Rich و Group."""
    # إنشاء جدول الأوامر
    cmd_table = Table(show_header=False, box=None, padding=(0, 2))
    cmd_table.add_column("⚡", style="bold cyan", width=3)
    cmd_table.add_column("Command", style="bold green")
    cmd_table.add_column("→", style="dim", width=2)
    cmd_table.add_column("Description", style="white")

    cmd_table.add_row("", "Miou export --type admin", "→", "Save admin URLs to file")
    cmd_table.add_row("", "Miou export --format burp", "→", "Generate Burp Suite list")
    cmd_table.add_row("", "Miou review", "→", "Review low-confidence items")
    cmd_table.add_row("", "Miou start --clean", "→", "Start fresh session")
    cmd_table.add_row("", "Miou export --format csv", "→", "Export as CSV for reports")
    cmd_table.add_row("", "Miou --help", "→", "Show all options")

    # تلميح صغير في الأسفل
    tip = Text("💡 Tip: Use 'Miou --help' for all options", style="dim")
    tip_group = Group(cmd_table, tip)

    return Panel(tip_group, title="🚀 Quick Actions", border_style="green", height=14)

def build_layout():
    layout = Layout()
    layout.split(
        Layout(name="header", size=12),
        Layout(name="body"),
        Layout(name="logs", size=12),
        Layout(name="footer", size=6)
    )
    layout["body"].split_row(
        Layout(name="tools_table", ratio=2),
        Layout(name="quick_actions", ratio=1)
    )
    logo_text = Text.from_ansi(LOGO)
    layout["header"].update(Panel(logo_text, border_style="bright_blue"))
    
    active_tools_list = get_active_tools_list()
    tools_table = build_tools_table(active_tools_list)
    layout["tools_table"].update(Panel(tools_table, title="🛠️ Active Recon Tools", border_style="cyan"))
    
    quick_actions_panel = build_quick_actions_panel()
    layout["quick_actions"].update(quick_actions_panel)
    
    logs_panel = build_logs_panel()
    layout["logs"].update(logs_panel)
    
    stats_panel = build_stats_panel(active_tools_list)
    layout["footer"].update(stats_panel)
    return layout

def clean_organized():
    if os.path.exists(ORGANIZED_DIR):
        shutil.rmtree(ORGANIZED_DIR)
    os.makedirs(ORGANIZED_DIR, exist_ok=True)
    add_log("🧹 Cleaned old organized data", "yellow")

def start_dashboard(clean_start=False):
    global previous_running_tools
    if clean_start:
        clean_organized()
    else:
        os.makedirs(ORGANIZED_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    previous_running_tools = get_running_recon_tools()
    add_log("🚀 Dashboard started", "cyan")
    print(f"🚀 Professional Dashboard started. Fallback timeout: {FALLBACK_TIMEOUT}s")
    with Live(build_layout(), refresh_per_second=2, screen=True) as live:
        try:
            while True:
                update_tool_status_logs()
                live.update(build_layout())
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            add_log("🛑 Dashboard stopped by user", "red")
            pass