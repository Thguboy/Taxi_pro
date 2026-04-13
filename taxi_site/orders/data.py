from __future__ import annotations

import random
from pathlib import Path
import sys

# Make shared package importable when running manage.py from project root
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from shared.drivers import Driver, DRIVERS  # noqa: E402


def drivers_sorted() -> list[Driver]:
    return sorted(DRIVERS, key=lambda d: d.price)


def random_eta() -> int:
    """Return estimated arrival time in minutes."""
    return random.randint(5, 15)
