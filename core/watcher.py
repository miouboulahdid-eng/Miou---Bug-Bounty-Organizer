import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.auto_parser import auto_detect_and_parse
from config import RAW_DIR

class WatcherHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_processed = {}
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_event(event.src_path)
    def on_created(self, event):
        if not event.is_directory:
            self._handle_event(event.src_path)
    def _handle_event(self, path):
        now = time.time()
        if path in self.last_processed and now - self.last_processed[path] < 1:
            return
        self.last_processed[path] = now
        auto_detect_and_parse(path)

def start_watcher():
    print("🔍 Watching for new files...")
    os.makedirs(RAW_DIR, exist_ok=True)
    observer = Observer()
    observer.schedule(WatcherHandler(), RAW_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()