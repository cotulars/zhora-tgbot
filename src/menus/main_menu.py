from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton, CallbackQuery
from aiogram import Router, F

from src.app import bot, dp
from src.database.domain.settings_db import SettingsDB
from src.database.domain.users_db import UsersDB

router = Router()
dp.include_router(router)

@router.callback_query(F.data == "main")
async def handle_open_main_callback(callback: CallbackQuery):
    await menu_main(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.answer()


async def menu_main(chat_id, message_id=None):
    db = UsersDB()
    user = await db.get_user(chat_id)
    user_settings = await SettingsDB.get_settings(chat_id)

    with open(f"./src/assets/menu_localization/{user_settings.lang}/menu_main.txt", "r") as f:
        menu_text = f.read()

    menu_text = menu_text.format(user.name)

    settings_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Statistics", callback_data="statistics"), InlineKeyboardButton(text="Functions", callback_data="functions")],
            [InlineKeyboardButton(text="Settings", callback_data="settings")],
            [InlineKeyboardButton(text="About", callback_data="about")]
        ])

    if message_id:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=menu_text,
            reply_markup=settings_menu_keyboard
        )
    else:
        await bot.send_message(
            chat_id,
            menu_text,
            reply_markup=settings_menu_keyboard
        )

    await db.close()