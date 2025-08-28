\
#!/usr/bin/env bash
# run_gui.sh — Launch the Legal Converter GUI (macOS/Linux)
# Usage: ./run_gui.sh [/absolute/path/to/project]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${1:-$SCRIPT_DIR}"
cd "$PROJECT_DIR"

# Ensure virtual environment
if [[ ! -d ".venv" ]]; then
  echo "Creating virtual environment at $PROJECT_DIR/.venv ..."
  python3 -m venv .venv
  source .venv/bin/activate
  echo "Installing requirements ..."
  if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
  else
    pip install -U openai python-docx pdfplumber PyPDF2 reportlab tqdm
  fi
else
  source .venv/bin/activate
fi

# Check API key
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "ERROR: OPENAI_API_KEY is not set."
  echo "Set it (temporary): export OPENAI_API_KEY=\"sk-...\""
  echo "Or add it to ~/.zshrc and reopen Terminal."
  exit 3
fi

# Launch GUI
if [[ ! -f "legal_converter_gui.py" ]]; then
  echo "ERROR: Myinterface.py not found in $PROJECT_DIR"
  exit 4
fi

python3 Myinterface.py
