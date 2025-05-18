from datetime import timezone

from src.app import dp, bot
from src.database.domain.messages_db import MessagesDB
from src.database.domain.users_db import UsersDB
from src.database.model.message_entity import Message
from src.database.model.user_entity import User

from aiogram.types import Update
from aiogram.dispatcher.middlewares.base import BaseMiddleware

class PersistAllMessagesMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data):
        if event.message and event.message.chat.type in {"group", "supergroup"}:
            msg = event.message
            naive_utc_date = msg.date.astimezone(timezone.utc).replace(tzinfo=None)

            if (event.message.new_chat_members
                    and (bot.id in [member.id for member in event.message.new_chat_members])):
                return await handler(event, data)

            if not await UsersDB.is_user_exists(msg.from_user.id):
                udb = UsersDB()
                await udb.add_user(
                    User(
                        id=msg.from_user.id,
                        username=msg.from_user.username,
                        name=f'{msg.from_user.first_name} {msg.from_user.last_name or ""}'
                    )
                )
                await udb.close()

            await MessagesDB.add_message(
                Message(
                    chat_id=msg.chat.id,
                    msg_id=msg.message_id,
                    user_id=msg.from_user.id,
                    text=msg.text or "",
                    reply_to_msg_id=msg.reply_to_message.message_id if msg.reply_to_message else None,
                    date=naive_utc_date
                )
            )
        return await handler(event, data)

dp.update.middleware(PersistAllMessagesMiddleware())

print("On group message handler loaded")
