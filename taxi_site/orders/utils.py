import json
import os
import urllib.parse
import urllib.request
from typing import Optional

from .data import Driver


def send_order_to_telegram(
    *,
    driver: Driver,
    origin: str,
    destination: str,
    payment: str,
    note: str,
    eta_minutes: int,
) -> Optional[str]:
    """
    Forward order details to Telegram bot (optional).
    Requires BOT_TOKEN and BOT_CHAT_ID env vars.
    Returns error message string on failure, None on success or if disabled.
    """
    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("BOT_CHAT_ID")
    if not token or not chat_id:
        return None

    text = (
        "🚕 Yangi buyurtma\n"
        f"Haydovchi: {driver.full_name} ({driver.car})\n"
        f"Narxi: {driver.price:,} so'm\n"
        f"Qayerdan: {origin}\n"
        f"Qayerga: {destination}\n"
        f"To'lov: {payment}\n"
        f"Izoh: {note or '-'}\n"
        f"Yetib kelish: {eta_minutes} daqiqa (taxmin)."
    )

    url = (
        f"https://api.telegram.org/bot{token}/sendMessage?"
        + urllib.parse.urlencode({"chat_id": chat_id, "text": text})
    )
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            body = resp.read()
            data = json.loads(body)
            if not data.get("ok"):
                return str(data)
    except Exception as exc:  # noqa: BLE001
        return str(exc)
    return None
