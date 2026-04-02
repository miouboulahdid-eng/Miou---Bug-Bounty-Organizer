# 🐺 Miou - Bug Bounty Organizer

**Real-time dashboard to organize, classify, and monitor your bug bounty recon outputs.**
<img width="1602" height="811" alt="Screenshot_20260402_210044" src="https://github.com/user-attachments/assets/0aed6e47-8f80-40be-88f5-d4f9a5f8ede8" />
<img width="1646" height="859" alt="Screenshot_20260402_211222" src="https://github.com/user-attachments/assets/9ba35ebc-a5da-4628-81dd-23fca01a3086" />





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
