from aiogram import Dispatcher

from .chat_type_filter import ChatTypeFilter


def setup_filters(dp: Dispatcher) -> None:
    dp.message.filter(ChatTypeFilter())
    dp.callback_query.filter(ChatTypeFilter())
