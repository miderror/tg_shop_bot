import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

import config
from filters import setup_filters
from handlers import setup_handlers
from middlewares import setup_middlewares
from utils.api_handlers import yookassa_webhook_handler, set_bot_instance
from utils.yookassa_api import setup_yookassa_configuration


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(
        config.WEBHOOK_URL,
        secret_token=config.WEBHOOK_SECRET,
    )
    setup_yookassa_configuration()
    set_bot_instance(bot)


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()
    if bot.session:
        await bot.session.close()


def main() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    setup_filters(dp)
    setup_middlewares(dp)
    setup_handlers(dp)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config.WEBHOOK_SECRET
    ).register(app, path=config.WEBHOOK_PATH)

    app.router.add_post(config.WEBHOOK_YOOKASSA_PATH, yookassa_webhook_handler)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=config.WEB_SERVER_HOST, port=config.WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
