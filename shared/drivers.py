"""
Shared driver catalog used by both the Django site and the Telegram bot.
Prices are integers (so'm) for easy sorting; display formatting happens in callers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Driver:
    id: str
    full_name: str
    car: str
    phone: str
    price: int  # in so'm


DRIVERS: List[Driver] = [
    Driver(
        id="anvar",
        full_name="Anvar Alimov",
        car="Nexia",
        phone="+998 90 123 45 67",
        price=45000,
    ),
    Driver(
        id="umid",
        full_name="Umidbek Shakarboyev",
        car="Spark",
        phone="+998 97 000 12 45",
        price=30000,
    ),
    Driver(
        id="diyor",
        full_name="Diyorbek Toshkentov",
        car="Cobalt",
        phone="+998 97 111 22 33",
        price=20000,
    ),
    Driver(
        id="hojiboy",
        full_name="Hojiboy Murodov",
        car="Malibu 2",
        phone="+998 90 555 55 55",
        price=80000,
    ),
    Driver(
        id="malika",
        full_name="Malika Karimova",
        car="Tracker",
        phone="+998 91 555 12 34",
        price=60000,
    ),
]


def as_dict_list() -> list[dict]:
    """Return driver list as plain dicts for JSON responses."""
    return [
        {
            "id": d.id,
            "full_name": d.full_name,
            "car": d.car,
            "phone": d.phone,
            "price": d.price,
        }
        for d in DRIVERS
    ]
