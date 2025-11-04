"""
Laniakea Protocol - Configuration
تنظیمات پروتوکل
"""

import os
from typing import List, Tuple, Set
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیمات شبکه
HOST: str = "0.0.0.0"

# تنظیمات بلاک‌چین
BLOCK_REWARD: float = 10.0  # پاداش پایه برای ساخت بلاک
BLOCK_TIME: int = 20  # زمان بین بلاک‌ها (ثانیه)

# نودهای authority
AUTHORITY_NODES: Set[str] = set()


def get_bootstrap_nodes() -> List[Tuple[str, int]]:
    """
    دریافت لیست نودهای bootstrap از متغیر محیطی
    
    Returns:
        لیست (host, port)
    """
    nodes_str = os.getenv("BOOTSTRAP_NODES", "")
    if not nodes_str:
        return []

    nodes = []
    for node_str in nodes_str.split(','):
        try:
            host, port_str = node_str.strip().split(':')
            nodes.append((host, int(port_str)))
        except (ValueError, IndexError):
            pass

    return nodes


def is_authority() -> bool:
    """
    بررسی اینکه آیا این نود authority است
    
    Returns:
        True اگر authority باشد
    """
    return os.getenv("IS_AUTHORITY", "false").lower() == "true"


# تنظیمات Cognitive Core
COGNITIVE_MODEL = os.getenv("COGNITIVE_MODEL", "gpt-4.1-mini")

# تنظیمات شبیه‌سازی
SIMULATION_ENABLED = os.getenv("SIMULATION_ENABLED", "false").lower() == "true"
SIMULATION_SPEED = float(os.getenv("SIMULATION_SPEED", "1.0"))

# تنظیمات اقتصادی
TOKEN_INFLATION_RATE = float(os.getenv("TOKEN_INFLATION_RATE", "0.02"))
TOKEN_BURN_RATE = float(os.getenv("TOKEN_BURN_RATE", "0.01"))
STAKING_APY = float(os.getenv("STAKING_APY", "0.05"))
