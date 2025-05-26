from typing import Union

import texts
from aiogram import Router, F
from aiogram import html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboards.callback_data import BackCallback
from keyboards.inline_keyboards import main_menu_keyboard
from shop_app.models import TelegramUser
from utils.messages import update_or_send_message

router = Router()


@router.message(CommandStart())
@router.callback_query(BackCallback.filter(F.to == "main_menu"))
async def handle_main_menu(event: Union[Message, CallbackQuery], tg_user: TelegramUser, state: FSMContext):
    await state.clear()

    user_name = html.quote(tg_user.first_name) or texts.DEFAULT_USER_NAME

    await update_or_send_message(
        event,
        text=texts.WELCOME_MESSAGE.format(user_first_name=user_name),
        reply_markup=main_menu_keyboard()
    )
