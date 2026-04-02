#!/usr/bin/env python3
import argparse
import threading
import sys
import os
from core.watcher import start_watcher
from utils.dashboard import start_dashboard
from utils.logger import log_miou_command

def start_all(clean=False):
    cmd = "Miou start" + (" --clean" if clean else "")
    log_miou_command(cmd)
    print("🚀 Starting Bug Bounty Organizer (Watcher + Dashboard)...")
    if clean:
        from utils.dashboard import clean_organized
        clean_organized()
    watcher_thread = threading.Thread(target=start_watcher, daemon=True)
    watcher_thread.start()
    start_dashboard(clean_start=False)

def main():
    parser = argparse.ArgumentParser(description="Bug Bounty Organizer - Real-time Recon Data Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    start_parser = subparsers.add_parser("start", help="Start watcher + dashboard")
    start_parser.add_argument("--clean", action="store_true", help="Clean organized directory before starting")
    
    subparsers.add_parser("watch", help="Run only file watcher")
    
    dashboard_parser = subparsers.add_parser("dashboard", help="Run only dashboard UI")
    dashboard_parser.add_argument("--clean", action="store_true", help="Clean organized before starting")
    
    export_parser = subparsers.add_parser("export", help="Export filtered results")
    export_parser.add_argument("--type", help="Filter by type (admin, param, keys, etc.)")
    export_parser.add_argument("--tool", help="Filter by tool name")
    export_parser.add_argument("--regex", help="Regex pattern to match in URL")
    export_parser.add_argument("--format", choices=["txt", "csv", "json", "burp"], default="txt", help="Output format")
    export_parser.add_argument("--output", help="Output filename (optional)")
    
    subparsers.add_parser("review", help="Review and correct low-confidence classifications")
    
    args = parser.parse_args()
    
    if args.command == "export":
        cmd = f"Miou export --type {args.type} --tool {args.tool} --regex {args.regex} --format {args.format} --output {args.output}"
        log_miou_command(cmd)
        from core.exporter import export_results
        export_results(export_type=args.type, tool=args.tool, regex=args.regex, output_format=args.format, output_file=args.output)
    elif args.command == "review":
        log_miou_command("Miou review")
        from core.review import review_pending
        review_pending()
    elif args.command == "watch":
        log_miou_command("Miou watch")
        start_watcher()
    elif args.command == "dashboard":
        cmd = "Miou dashboard" + (" --clean" if args.clean else "")
        log_miou_command(cmd)
        start_dashboard(clean_start=args.clean)
    elif args.command == "start":
        start_all(clean=args.clean)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()