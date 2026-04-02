#!/usr/bin/env python3
import argparse
import threading
from core.watcher import start_watcher
from utils.dashboard import start_dashboard

def start_all(clean=False):
    print("🚀 Starting Bug Bounty Organizer (Watcher + Dashboard)...")
    if clean:
        from utils.dashboard import clean_organized
        clean_organized()
    watcher_thread = threading.Thread(target=start_watcher, daemon=True)
    watcher_thread.start()
    start_dashboard(clean_start=False)

def main():
    parser = argparse.ArgumentParser(description="Bug Bounty Organizer")
    parser.add_argument("mode", choices=["watch", "dashboard", "start"], help="Mode")
    parser.add_argument("--clean", action="store_true", help="Clean old data")
    args = parser.parse_args()

    if args.mode == "watch":
        start_watcher()
    elif args.mode == "dashboard":
        start_dashboard(clean_start=args.clean)
    elif args.mode == "start":
        start_all(clean=args.clean)

if __name__ == "__main__":
    main()