from datetime import timezone

from aiogram import Bot, types

from src.app import bot
from src.database.domain.messages_db import MessagesDB
from src.database.model.message_entity import Message

original_reply = types.Message.reply

async def custom_reply(self, text, *args, **kwargs) -> types.Message:
    message = await original_reply(self, text, *args, **kwargs)

    if message.chat.type not in {"group", "supergroup"}:
        return message

    naive_utc_date = message.date.astimezone(timezone.utc).replace(tzinfo=None)

    await MessagesDB.add_message(Message(
        chat_id=message.chat.id,
        msg_id=message.message_id,
        user_id=bot.id,
        text=text,
        reply_to_msg_id=self.message_id,
        date=naive_utc_date
    ))
    return message


types.Message.reply = custom_reply

print("Reply patch loaded")