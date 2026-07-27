#!/usr/bin/env python3
"""
Health check script for Python bridge
"""
import json
import sys

def main():
    result = {
        "status": "healthy",
        "version": "0.0.03",
        "python_version": sys.version,
    }
    print(json.dumps(result))
    return 0

if __name__ == "__main__":
    sys.exit(main())
