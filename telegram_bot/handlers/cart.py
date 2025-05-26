import config
import texts
from aiogram import Router, F, html
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.db import transaction
from keyboards.callback_data import BackCallback, DeleteCartCallback, OrderCallback
from keyboards.inline_keyboards import back_to_main_menu_keyboard
from shop_app.models import TelegramUser, Cart, Product, Order, OrderItem
from states import OrderStates
from utils.messages import update_or_send_message
from utils.yookassa_api import create_yookassa_payment

router = Router()


async def _get_cart_items_and_total_price(tg_user: TelegramUser):
    cart_items = await sync_to_async(list)(
        Cart.objects.filter(user=tg_user).select_related('product').order_by('product__name')
    )
    total_cart_price = sum(float(item.quantity) * float(item.product.price) for item in cart_items)
    return cart_items, total_cart_price


async def _build_cart_text(cart_items: list[Cart], total_cart_price: float) -> list[str]:
    messages = []
    current_text_buffer = texts.CART_HEADER_MESSAGE

    for i, item in enumerate(cart_items):
        item_total_price = float(item.quantity) * float(item.product.price)
        item_text = texts.CART_ITEM_TEMPLATE.format(
            item_number=i + 1,
            product_name=item.product.name,
            quantity=item.quantity,
            price=item.product.price,
            total_item_price=item_total_price
        )

        if len(current_text_buffer) + len(item_text) > config.MAX_MESSAGE_TEXT_LENGTH:
            messages.append(current_text_buffer)
            current_text_buffer = ""

        current_text_buffer += item_text

    if current_text_buffer:
        messages.append(current_text_buffer)

    summary_text = texts.CART_SUMMARY_TEMPLATE.format(total_cart_price=total_cart_price)

    if messages and len(messages[-1]) + len(summary_text) <= config.MAX_MESSAGE_TEXT_LENGTH:
        messages[-1] += "\n" + summary_text
    else:
        messages.append(summary_text)

    return messages


@router.callback_query(BackCallback.filter(F.to == "cart"))
async def show_cart(callback: CallbackQuery, state: FSMContext, tg_user: TelegramUser):
    await state.clear()

    cart_items, total_cart_price = await _get_cart_items_and_total_price(tg_user)

    if not cart_items:
        await update_or_send_message(
            event=callback,
            text=texts.EMPTY_CART_MESSAGE,
            reply_markup=back_to_main_menu_keyboard()
        )
        return

    cart_texts = await _build_cart_text(cart_items, total_cart_price)

    for i in range(len(cart_texts) - 1):
        await update_or_send_message(
            event=callback,
            text=cart_texts[i],
            force_new=True,
            reply_markup=None
        )

    await update_or_send_message(
        event=callback,
        text=cart_texts[-1],
        reply_markup=await _get_cart_main_keyboard(),
        force_new=bool(len(cart_texts) > 1)
    )


async def _get_cart_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=texts.CART_DELETE_BUTTON, callback_data=DeleteCartCallback().pack()))
    builder.row(InlineKeyboardButton(text=texts.CART_CLEAR_ALL_BUTTON,
                                     callback_data=DeleteCartCallback(delete_all=True).pack()))
    builder.row(InlineKeyboardButton(text=texts.CART_CHECKOUT_BUTTON, callback_data=OrderCallback().pack()))
    builder.row(InlineKeyboardButton(text=texts.BACK_TO_MENU_BUTTON, callback_data=BackCallback(to="main_menu").pack()))
    return builder.as_markup()


async def _get_delete_mode_keyboard(
        cart_items: list[Cart],
        current_page: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    items_per_page = config.ITEMS_PER_PAGE
    start_index = current_page * items_per_page
    end_index = start_index + items_per_page

    items_on_page = cart_items[start_index:end_index]

    for item in items_on_page:
        builder.row(InlineKeyboardButton(
            text=f"{texts.CART_REMOVE_ITEM_BUTTON_PREFIX}{item.product.name} ({item.quantity} шт.)",
            callback_data=DeleteCartCallback(page=current_page, cart_item_id=item.id).pack()
        ))

    nav_row = []
    if current_page > 0:
        nav_row.append(InlineKeyboardButton(text=texts.PAGINATION_PREV_BUTTON,
                                            callback_data=DeleteCartCallback(page=current_page - 1).pack()))
    if end_index < len(cart_items):
        nav_row.append(InlineKeyboardButton(text=texts.PAGINATION_NEXT_BUTTON,
                                            callback_data=DeleteCartCallback(page=current_page + 1).pack()))
    if nav_row:
        builder.row(*nav_row)

    builder.row(
        InlineKeyboardButton(text=texts.CART_COMPLETE_DELETE_BUTTON, callback_data=BackCallback(to="cart").pack()))
    return builder.as_markup()


@router.callback_query(DeleteCartCallback.filter(F.cart_item_id.is_(None) and F.delete_all.is_(False)))
async def prompt_delete_cart_items(callback: CallbackQuery, state: FSMContext, tg_user: TelegramUser,
                                   callback_data: DeleteCartCallback):
    cart_items, _ = await _get_cart_items_and_total_price(tg_user)

    if not cart_items:
        await update_or_send_message(
            event=callback,
            text=texts.EMPTY_CART_MESSAGE,
            reply_markup=back_to_main_menu_keyboard()
        )
        return

    current_page = callback_data.page if callback_data.page is not None else 0

    await update_or_send_message(
        event=callback,
        text=texts.CART_PROMPT_DELETE_MESSAGE,
        reply_markup=await _get_delete_mode_keyboard(cart_items, current_page)
    )


@router.callback_query(DeleteCartCallback.filter(F.delete_all.is_(False)))
async def delete_cart_item(callback: CallbackQuery, state: FSMContext, callback_data: DeleteCartCallback,
                           tg_user: TelegramUser):
    deleted_count = await sync_to_async(Cart.objects.filter(id=callback_data.cart_item_id, user=tg_user).delete)()
    if deleted_count[0] > 0:
        await callback.answer(texts.CART_ITEM_DELETED_MESSAGE, show_alert=True)
    await prompt_delete_cart_items(callback, state, tg_user, DeleteCartCallback(page=callback_data.page))


@router.callback_query(DeleteCartCallback.filter(F.delete_all.is_(True)))
async def clear_full_cart(callback: CallbackQuery, state: FSMContext, tg_user: TelegramUser):
    await sync_to_async(Cart.objects.filter(user=tg_user).delete)()
    await callback.answer(texts.CART_CLEARED_MESSAGE, show_alert=True)
    await show_cart(callback, state, tg_user)


@router.callback_query(OrderCallback.filter(F.is_confirm.is_(False)))
async def start_checkout(callback: CallbackQuery, state: FSMContext, tg_user: TelegramUser):
    cart_items, _ = await _get_cart_items_and_total_price(tg_user)
    if not cart_items:
        await show_cart(callback, state, tg_user)
        return

    await state.set_state(OrderStates.waiting_for_delivery_info)

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(
        InlineKeyboardButton(text=texts.CANCEL_BUTTON_TEXT, callback_data=BackCallback(to="cart").pack()))

    await update_or_send_message(
        event=callback,
        text=texts.ORDER_ENTER_DELIVERY_INFO_TEXT,
        reply_markup=keyboard_builder.as_markup()
    )


@router.message(OrderStates.waiting_for_delivery_info)
async def process_delivery_info_text(message: Message, state: FSMContext):
    delivery_info = html.quote(message.text.strip())

    if not delivery_info:
        await message.answer(text=texts.ORDER_EMPTY_DELIVERY_INFO_MESSAGE)
        return

    order_summary_text = texts.ORDER_CONFIRMATION_PROMPT.format(delivery_info=delivery_info)

    await state.update_data(delivery_info=delivery_info)
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(
        InlineKeyboardButton(text=texts.CONFIRM_BUTTON_TEXT, callback_data=OrderCallback(is_confirm=True).pack()))
    keyboard_builder.row(
        InlineKeyboardButton(text=texts.CANCEL_BUTTON_TEXT, callback_data=BackCallback(to="cart").pack()))

    await update_or_send_message(
        event=message,
        text=order_summary_text,
        reply_markup=keyboard_builder.as_markup()
    )


@router.callback_query(OrderCallback.filter(F.is_confirm.is_(True)))
async def confirm_and_initiate_payment(callback: CallbackQuery, callback_data: OrderCallback, state: FSMContext,
                                       tg_user: TelegramUser):
    state_data = await state.get_data()
    delivery_info = state_data.get('delivery_info')

    if not delivery_info:
        await update_or_send_message(
            event=callback,
            text=texts.ORDER_MISSING_DELIVERY_INFO_MESSAGE,
            reply_markup=back_to_main_menu_keyboard()
        )
        return

    await update_or_send_message(event=callback, text=texts.ORDER_PROCESSING_MESSAGE, reply_markup=None)

    cart_items, total_cart_price = await _get_cart_items_and_total_price(tg_user)

    if not cart_items:
        await update_or_send_message(
            event=callback,
            text=texts.CART_EMPTY_FOR_CHECKOUT_MESSAGE,
            reply_markup=back_to_main_menu_keyboard()
        )
        return

    try:
        @sync_to_async
        def create_order_in_db():
            with transaction.atomic():
                order_obj = Order.objects.create(
                    user=tg_user,
                    delivery_info=delivery_info,
                    total_amount=total_cart_price,
                    payment_status=Order.STATUS_PENDING
                )

                order_items_to_create = []
                for item in cart_items:
                    product_obj = Product.objects.get(id=item.product.id)
                    order_items_to_create.append(OrderItem(
                        order=order_obj,
                        product=product_obj,
                        quantity=item.quantity,
                        price_at_purchase=item.product.price
                    ))
                OrderItem.objects.bulk_create(order_items_to_create)
                return order_obj

        order_obj = await create_order_in_db()

        yookassa_payment = await create_yookassa_payment(
            amount=float(total_cart_price),
            description=texts.YOOKASSA_PAYMENT_DESCRIPTION.format(order_id=order_obj.id),
            order_id=order_obj.id,
            telegram_user_id=tg_user.id
        )

        order_obj.yookassa_payment_id = yookassa_payment.id
        await sync_to_async(order_obj.save)()

        await sync_to_async(Cart.objects.filter(user=tg_user).delete)()

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text=texts.PAYMENT_BUTTON_TEXT, url=yookassa_payment.confirmation.confirmation_url))
        keyboard = builder.as_markup()
        await update_or_send_message(
            event=callback,
            text=texts.ORDER_PAYMENT_REQUIRED_MESSAGE.format(order_id=order_obj.id),
            reply_markup=keyboard
        )
    except Exception as e:
        await update_or_send_message(
            event=callback,
            text=texts.ORDER_CREATION_ERROR_MESSAGE,
            reply_markup=back_to_main_menu_keyboard()
        )
