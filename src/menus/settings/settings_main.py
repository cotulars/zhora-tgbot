from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton, CallbackQuery
from aiogram import Router, F

from src.app import bot, dp

router = Router()
dp.include_router(router)

@router.callback_query(F.data == "settings_main")
async def handle_open_settings_callback(callback: CallbackQuery):
    await menu_settings_main(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.answer()

async def menu_settings_main(chat_id, message_id=None):
    settings_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Account", callback_data="settings_account"), InlineKeyboardButton(text="Notifications", callback_data="settings_notifications")],
            [InlineKeyboardButton(text="Chats Settings", callback_data="settings_chats")],
            [InlineKeyboardButton(text="Back", callback_data="settings_back")]
        ])

    if message_id:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Settings menu",
            reply_markup=settings_menu_keyboard
        )
    else:
        await bot.send_message(
            chat_id,
            "Settings menu",
            reply_markup=settings_menu_keyboard
        )