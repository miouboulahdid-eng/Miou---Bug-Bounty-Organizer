#!/bin/bash
set -e

echo "🐺 Installing Miou Bug Bounty Organizer..."

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.6+"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Create launcher in ~/.local/bin
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/Miou" << EOF
#!/bin/bash
$SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/cli.py "\$@"
EOF
chmod +x "$HOME/.local/bin/Miou"

# Add to PATH if needed
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    SHELL_CONFIG=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    fi
    if [ -n "$SHELL_CONFIG" ]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_CONFIG"
        echo "✅ Added ~/.local/bin to PATH in $SHELL_CONFIG"
    else
        echo "⚠️ Please manually add ~/.local/bin to your PATH"
    fi
fi

echo ""
echo "✅ Installation complete!"
echo "🚀 Please run: source ~/.bashrc  (or restart your terminal)"
echo "   Then type: Miou start"