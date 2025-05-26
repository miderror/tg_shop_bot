from datetime import datetime
from typing import Callable, Dict, Any, Awaitable

import config
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from django.utils import timezone
from shop_app.models import TelegramUser


class UserExistenceMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        tg_id = event.from_user.id
        first_name = event.from_user.first_name
        last_name = event.from_user.last_name
        username = event.from_user.username

        user, created = await sync_to_async(TelegramUser.objects.get_or_create)(
            id=tg_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
            }
        )

        current_time = datetime.now(tz=timezone.get_current_timezone())
        if not created and current_time - user.updated_at > config.USER_UPDATE_INTERVAL:
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            await sync_to_async(user.save)()

        data['tg_user'] = user

        return await handler(event, data)
