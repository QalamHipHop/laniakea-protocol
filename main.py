#!/usr/bin/env python3
"""
LaniakeA Protocol - Main Entry Point
8-Dimensional Blockchain with AI Intelligence
Version: 3.0.0
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set environment variable for port (Render compatibility)
PORT = int(os.getenv("PORT", 8000))

def main():
    """Main entry point"""
    try:
        # Import CLI
        from laniakea.cli.commands import cli
        
        # If PORT is set (e.g., by Render), start server automatically
        if "PORT" in os.environ:
            print(f"🚀 Starting LaniakeA Protocol on port {PORT}")
            sys.argv = [
                'laniakea',
                'start',
                '--host', '0.0.0.0',
                '--port', str(PORT),
                '--node-id', os.getenv('NODE_ID', 'laniakea-render-node')
            ]
        
        # Run CLI
        cli()
        
    except KeyboardInterrupt:
        print("\n🛑 LaniakeA Protocol stopped gracefully")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
