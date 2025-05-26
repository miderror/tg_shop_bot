from aiogram import Dispatcher

from .subscription_middleware import SubscriptionCheckMiddleware
from .user_middleware import UserExistenceMiddleware


def setup_middlewares(dp: Dispatcher) -> None:
    dp.message.outer_middleware(UserExistenceMiddleware())
    dp.callback_query.outer_middleware(UserExistenceMiddleware())

    dp.message.middleware(SubscriptionCheckMiddleware())
    dp.callback_query.middleware(SubscriptionCheckMiddleware())
