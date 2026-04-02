# 🐺 Miou - Bug Bounty Organizer

**Real-time dashboard to organize, classify, and monitor your bug bounty recon outputs.**
<img width="1250" height="774" alt="Screenshot_20260402_161018" src="https://github.com/user-attachments/assets/0cf000ee-3008-4c13-9cbd-117247e48ba5" />


*(Add your screenshot here)*

## ✨ Features

- 🔍 **Auto-detects** any recon tool (subfinder, httpx, nuclei, gau, etc.)
- 📂 **Organizes data** by tool and date: `data/organized/tool_YYYY-MM-DD/type.json`
- 🏷️ **Classifies** data into: `admin`, `param`, `keys`, `cookies`, `headers`, `vuln`, `other`
- 📊 **Live dashboard** with emojis, statistics, and process monitoring
- ⚡ **Smart process detection** – tools appear as soon as they start
- 💡 **Helpful tips** when no tools are active
- 🧹 **Clean mode** with `--clean` flag

## 🚀 Quick Install

```bash
git clone https://github.com/yourusername/bugbounty-organizer.git
cd bugbounty-organizer
chmod +x install.sh
./install.sh
source ~/.bashrc
