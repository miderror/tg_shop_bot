from typing import Callable, Dict, Any, Awaitable

import config
import texts
from aiogram import BaseMiddleware, Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import Message, CallbackQuery
from keyboards.inline_keyboards import get_subscription_keyboard


class SubscriptionCheckMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        tg_id = event.from_user.id
        bot: Bot = data['bot']

        unsubscribed_chat_ids = []
        for chat_id in config.REQUIRED_CHAT_IDS:
            member = await event.bot.get_chat_member(chat_id, tg_id)
            if member.status == ChatMemberStatus.LEFT:
                unsubscribed_chat_ids.append(chat_id)

        if unsubscribed_chat_ids:
            if isinstance(event, Message):
                message: Message = event
            elif isinstance(event, CallbackQuery):
                message: Message = event.message
                await event.answer()
            return await message.answer(
                texts.SUBSCRIPTION_REQUIRED_MESSAGE,
                reply_markup=await get_subscription_keyboard(bot, unsubscribed_chat_ids)
            )
        return await handler(event, data)
