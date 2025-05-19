import json

from src.database.domain.messages_db import MessagesDB
from src.database.domain.users_db import UsersDB


cotext_caching = {}

async def generate_message_context(chat_id, count = 100, tag='default', threshold=100) -> str:

    if cotext_caching.get(tag, None):
        messages = await MessagesDB.get_messages_from_msg_id_to_latest(chat_id, cotext_caching[tag])
        if len(messages) > (threshold+count):
            messages = await MessagesDB.get_messages(chat_id=chat_id, count=count)
            cotext_caching[tag] = messages[-1].msg_id
    else:
        messages = await MessagesDB.get_messages(chat_id=chat_id, count=count)
        cotext_caching[tag] = messages[-1].msg_id

    users_cache = {}

    users_db = UsersDB()

    request = []

    for msg in messages:
        if msg.user_id not in users_cache:
            users_cache[msg.user_id] = await users_db.get_user(msg.user_id)

        message_dict = {
            'id': msg.msg_id,
            'from': {
                'name': users_cache[msg.user_id].name,
                'username': users_cache[msg.user_id].username,
                'id': users_cache[msg.user_id].id
            },
            'reply_to': msg.reply_to_msg_id if msg.reply_to_msg_id else None,
            'text': msg.text,
            'date': str(msg.date)
        }
        request.append(message_dict)

    await users_db.close()

    return json.dumps(request)