from datetime import timezone

from aiogram import Bot, types

from src.app import bot
from src.database.domain.messages_db import MessagesDB
from src.database.model.message_entity import Message

original_send_message = Bot.send_message

async def custom_send_message(self, chat_id, text, *args, **kwargs) -> types.Message:
    message = await original_send_message(self, chat_id, text, *args, **kwargs)

    naive_utc_date = message.date.astimezone(timezone.utc).replace(tzinfo=None)

    await MessagesDB.add_message(Message(
        chat_id=chat_id,
        msg_id=message.message_id,
        user_id=bot.id,
        text=text,
        date=naive_utc_date
    ))
    return message

Bot.send_message = custom_send_message

print("Send message patch loaded")