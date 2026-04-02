import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
ORGANIZED_DIR = os.path.join(BASE_DIR, "data", "organized")
BURP_DIR = os.path.join(BASE_DIR, "data", "burp")
EXPORTS_DIR = os.path.join(BASE_DIR, "data", "exports")
LOGS_DIR = os.path.join(BASE_DIR, "data", "logs")
CLASSIFICATION_DB = os.path.join(BASE_DIR, "data", "classification.db")