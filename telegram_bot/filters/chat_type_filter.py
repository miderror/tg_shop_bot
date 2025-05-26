from aiogram.enums import ChatType
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery


class ChatTypeFilter(Filter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        if isinstance(message, CallbackQuery):
            message = message.message

        return message.chat.type == ChatType.PRIVATE
