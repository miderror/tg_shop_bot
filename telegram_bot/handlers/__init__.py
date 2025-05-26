from aiogram import Dispatcher

from .cart import router as cart_router
from .catalog import router as catalog_router
from .faq import router as faq_router
from .start import router as start_router


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_routers(
        start_router,
        catalog_router,
        cart_router,
        faq_router,
    )
