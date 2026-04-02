import json
import yaml
import os

CONFIG_FILE = "config.yaml"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"tools": {}}
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f) or {"tools": {}}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

def add_tool(name, path):
    config = load_config()
    config["tools"][name] = {"enabled": True, "watch_path": path}
    save_config(config)
    print(f"✅ Tool {name} added and enabled")

def remove_tool(name):
    config = load_config()
    if name in config["tools"]:
        del config["tools"][name]
        save_config(config)
        print(f"❌ Tool {name} removed")
    else:
        print(f"⚠ Tool {name} not found")

def enable_tool(name):
    config = load_config()
    if name in config["tools"]:
        config["tools"][name]["enabled"] = True
        save_config(config)
        print(f"✅ Tool {name} enabled")
    else:
        print(f"⚠ Tool {name} not found")

def disable_tool(name):
    config = load_config()
    if name in config["tools"]:
        config["tools"][name]["enabled"] = False
        save_config(config)
        print(f"❌ Tool {name} disabled")
    else:
        print(f"⚠ Tool {name} not found")