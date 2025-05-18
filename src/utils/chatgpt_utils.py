from src.database.domain.messages_db import MessagesDB
from src.database.domain.users_db import UsersDB


async def generate_message_context(chat_id, count = 50) -> str:
    messages = await MessagesDB.get_messages(chat_id=chat_id, count=count)
    users_cache = {}

    users_db = UsersDB()

    request = ''

    for msg in messages:
        if msg.user_id not in users_cache:
            users_cache[msg.user_id] = await users_db.get_user(msg.user_id)

        request += '\n'
        request += f'id: {msg.msg_id}\n'
        request += f'from: {users_cache[msg.user_id].name} ({users_cache[msg.user_id].username}) <{users_cache[msg.user_id].id}>\n'
        request += f'reply to: {msg.reply_to_msg_id}\n' if msg.reply_to_msg_id else ''
        request += f'text: "{msg.text}"\n'
        request += f'date: {msg.date}\n'
        request += f'\n'

    await users_db.close()

    return request