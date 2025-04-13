from aiogram import types, Router, F
from aiogram.types import Message
from aiogram.dispatcher.dispatcher import Dispatcher

router = Router()

@router.message(F.text.regexp(r"^(міни|казино|вг|рулетка|кубики).*"))
async def handle_no_slash_commands(message: Message, dispatcher: Dispatcher):
    command_text = "/" + message.text  # додаємо слеш

    # Створюємо новий апдейт з текстом команди
    fake_update = types.Update(update_id=message.message_id, message=Message.model_construct(
        message_id=message.message_id,
        from_user=message.from_user,
        chat=message.chat,
        date=message.date,
        text=command_text
    ))

    # Обробляємо фейковий апдейт
    await dispatcher.feed_update(bot=message.bot, update=fake_update)
