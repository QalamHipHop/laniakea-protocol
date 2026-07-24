"""
Backward-compatibility shim for legacy Render deployments that treat ``src/``
as the project root. Newer Render blueprints use the repo root (this file is
present so older deploys keep working).
"""

import os
import sys

# Ensure repo root is on sys.path even if Render runs from inside ``src/``.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Delegate to the real entry point at the repo root.
from main import main  # noqa: E402

if __name__ == "__main__":
    main()
