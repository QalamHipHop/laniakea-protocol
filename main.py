#!/usr/bin/env python3
"""
LaniakeA Protocol - Main Entry Point
Unified intelligent blockchain system
Version: 3.0.0
"""

import sys
from pathlib import Path

# Add laniakea to path
sys.path.insert(0, str(Path(__file__).parent))

from laniakea.cli.commands import cli

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        print("\n🛑 LaniakeA Protocol stopped gracefully")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
