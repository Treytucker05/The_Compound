"""
main.py — Entry point for the COMPOUND_APPROACH Portal launcher.

Usage:
    python launcher/main.py

Or from the project root:
    python -m launcher.main
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from launcher.app import main

if __name__ == "__main__":
    main()
