from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

from src.app import bot


async def menu_settings_main(chat_id, message_id):
    await bot.send_message(
        chat_id,
        "Settings menu",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Change language", callback_data="change_lang")],
        ])
    )