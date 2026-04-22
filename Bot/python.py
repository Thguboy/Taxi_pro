    # Telegram aiogram bot online taxi zakaz qilish uchun bot
import asyncio
import logging
import random
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

# Make shared driver catalog importable when running from Bot/ directory
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from shared.drivers import DRIVERS  # noqa: E402

API_TOKEN = "8710352707:AAFhuNY-lZpKDXmq8oyX8plEOxtKuoGlBHI"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Handlers are grouped in a router (aiogram v3 style)
router = Router()

# Temporarily keep selections in memory per user
USER_DRIVER: dict[int, str] = {}
# Track per-user ETA timers so repeated orders cancel old countdowns
USER_TIMERS: dict[int, asyncio.Task] = {}


@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Xush kelibsiz! Taksi buyurtma berish uchun /order buyrug'ini bering."
    )


@router.message(Command("order"))
async def order_command(message: types.Message):
    driver_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🚕 {drv.full_name} | {drv.price:,} so'm",
                    callback_data=f"driver_{drv.id}",
                )
            ]
            for drv in DRIVERS
        ]
    )

    await message.answer(
        "Haydovchini tanlang (narxi ko'rsatilgan). Lokatsiya keyin so'raladi:",
        reply_markup=driver_kb,
    )


@router.message(F.location)
async def handle_location(message: types.Message):
    user_id = message.from_user.id if message.from_user else None
    driver_id = USER_DRIVER.get(user_id)
    if not driver_id:
        await message.answer(
            "Avval haydovchini tanlang: /order",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    driver = next((d for d in DRIVERS if d.id == driver_id), None)
    if not driver:
        await message.answer("Tanlangan haydovchi topilmadi, qayta urinib ko'ring.")
        return

    # Cancel old timer if user sends a new location/order
    old_task = USER_TIMERS.pop(user_id, None)
    if old_task and not old_task.done():
        old_task.cancel()

    eta_minutes = random.randint(5, 15)

    text = (
        f"🚕 {driver.full_name}\n"
        f"Mashina: {driver.car}\n"
        f"Telefon: {driver.phone}\n"
        f"To'lov: {driver.price:,} so'm\n"
        f"Lokatsiya qabul qilindi, haydovchi yo'lda.\n"
        f"Taxminiy yetib kelish: {eta_minutes} daqiqa."
    )
    await message.answer(text, reply_markup=ReplyKeyboardRemove())

    # Fire-and-forget timer for updates
    USER_TIMERS[user_id] = asyncio.create_task(
        start_eta_timer(bot=message.bot, chat_id=message.chat.id, eta_minutes=eta_minutes)
    )


@router.message()
async def echo_message(message: types.Message):
    await message.answer("Buyurtma uchun /order bosing.")


@router.callback_query()
async def handle_callbacks(call: types.CallbackQuery):
    if call.data and call.data.startswith("driver_"):
        driver_id = call.data.removeprefix("driver_")
        user_id = call.from_user.id if call.from_user else None
        USER_DRIVER[user_id] = driver_id

        kb = ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            keyboard=[
                [KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)]
            ],
        )

        await call.message.answer(
            "Tanlov qabul qilindi. Buyurtmani yakunlash uchun lokatsiya yuboring.",
            reply_markup=kb,
        )
    await call.answer()


async def start_eta_timer(bot: Bot, chat_id: int, eta_minutes: int) -> None:
    """
    Send countdown updates and a final arrival notification.
    """
    half = max(1, eta_minutes // 2)
    try:
        await asyncio.sleep(half * 60)
        remaining = eta_minutes - half
        if remaining > 0:
            await bot.send_message(
                chat_id,
                f"⏳ Haydovchi {remaining} daqiqada yetib keladi (taxmin).",
            )

        await asyncio.sleep(remaining * 60)
        await bot.send_message(
            chat_id, "✅ Haydovchi manzilga yetib keldi deb taxmin qilindi."
        )
    except asyncio.CancelledError:
        # Cancelled because user started a new order
        return


async def main() -> None:
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    # start polling; drop pending updates is handled by default webhook removal
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
