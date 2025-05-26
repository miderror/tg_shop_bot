from typing import Union

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InputFile


async def update_or_send_message(
        event: Union[Message, CallbackQuery],
        text: str | None = None,
        reply_markup: InlineKeyboardMarkup = None,
        parse_mode: Union[ParseMode, str] = ParseMode.HTML,
        photo: Union[str, InputFile] = None,
        caption: str = None,
        force_new: bool = False
) -> Message:
    message_to_edit: Message = None
    if isinstance(event, CallbackQuery):
        message_to_edit = event.message
        await event.answer()

    try:
        if photo:
            if message_to_edit:
                try:
                    await message_to_edit.delete()
                except TelegramAPIError as e:
                    pass
            return await event.bot.send_photo(
                chat_id=event.from_user.id,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        elif message_to_edit and not force_new:
            try:
                return await message_to_edit.edit_text(
                    text=text or caption,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            except TelegramAPIError as e:
                pass
        elif message_to_edit and force_new:
            try:
                await message_to_edit.delete()
            except TelegramAPIError as e:
                pass

        return await event.bot.send_message(
            chat_id=event.from_user.id,
            text=text or caption,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except TelegramAPIError as e:
        print(e)
        return await event.bot.send_message(
            chat_id=event.from_user.id,
            text=text or caption,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
