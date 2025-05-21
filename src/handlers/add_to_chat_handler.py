from aiogram import Router
from aiogram.types import Message
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from aiogram.types import ChatMemberUpdated

from src.app import dp, bot
from src.database.domain.chats_db import ChatsDB
from src.database.model.chat_entity import Chat

# Create a router for chat member updates
router = Router()
dp.include_router(router)



@router.my_chat_member()
async def on_added_to_chat(event: ChatMemberUpdated):
    if event.new_chat_member.user.id == bot.id:
        await ChatsDB.add_chat(
            Chat(
                id=event.chat.id,
                type=event.chat.type,
                title=event.chat.title,
                members_count=await event.chat.get_member_count(),
                isForum=event.chat.is_forum
            )
        )
        await bot.send_message(event.chat.id, "Жора на связи")

print("Added to chat handler loaded")
