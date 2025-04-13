from aiogram import Router, F
from aiogram.types import Message

router = Router()
router.message.filter(F.chat.type.in_({"group", "supergroup"}))

@router.message()
async def handle_group_messages(message: Message):
    if message.text and (message.text.startswith("/start") or message.text.startswith("/help")):
        await message.reply(
            "🤖 Бот працює і в групах!\nВикористовуйте команди або запускайте ігри 🎮"
        )
