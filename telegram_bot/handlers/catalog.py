from typing import Union
from typing import Union

import config
import texts
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile
from asgiref.sync import sync_to_async
from django.db import transaction
from keyboards.callback_data import CategoryCallback, SubcategoryCallback, ProductCallback, BackCallback, \
    AddToCartCallback
from keyboards.inline_keyboards import get_categories_keyboard, get_subcategories_keyboard, get_products_keyboard, \
    get_products_batch_keyboard, get_confirm_quantity_keyboard
from keyboards.inline_keyboards import (
    main_menu_keyboard,
)
from shop_app.models import Category, Subcategory, Product, Cart, TelegramUser
from states import CartStates
from utils.messages import update_or_send_message

from .cart import show_cart

router = Router()


@router.callback_query(CategoryCallback.filter())
async def show_categories(callback: CallbackQuery, callback_data: CategoryCallback, state: FSMContext):
    await callback.answer()
    categories = await sync_to_async(list)(Category.objects.all())

    keyboard = await get_categories_keyboard(categories, callback_data.page)
    message_text = texts.CATALOG_SELECT_CATEGORY if categories else texts.CATALOG_NO_CATEGORIES

    await update_or_send_message(event=callback, text=message_text, reply_markup=keyboard)


@router.callback_query(SubcategoryCallback.filter())
async def paginate_categories(callback: CallbackQuery, callback_data: SubcategoryCallback, state: FSMContext):
    await callback.answer()
    subcategories_qs = Subcategory.objects.filter(category_id=callback_data.category_id).select_related('category')
    subcategories = await sync_to_async(list)(subcategories_qs.all())

    keyboard = await get_subcategories_keyboard(callback_data.category_id, subcategories, callback_data.page)
    message_text = texts.CATALOG_SELECT_SUBCATEGORY if subcategories else texts.CATALOG_NO_SUBCATEGORIES

    await update_or_send_message(event=callback, text=message_text, reply_markup=keyboard)


@router.callback_query(ProductCallback.filter())
async def show_products(callback: CallbackQuery, callback_data: ProductCallback, state: FSMContext):
    subcategory = await sync_to_async(Subcategory.objects.select_related('category').get)(
        id=callback_data.subcategory_id
    )
    category_id_for_back = subcategory.category.id

    products_qs = Product.objects.filter(
        subcategory_id=callback_data.subcategory_id
    ).select_related('subcategory__category')
    products = await sync_to_async(list)(products_qs.all())

    if products and callback_data.offset <= len(products):
        await _send_products_batch(callback, products, callback_data.offset)

    keyboard = await get_products_keyboard(
        subcategory_id=callback_data.subcategory_id,
        products=products,
        offset=callback_data.offset,
        category_id_for_back=category_id_for_back
    )

    if products:
        has_more = callback_data.offset + config.ITEMS_PER_PAGE < len(products)
        message_text = texts.CATALOG_SHOW_MORE_PRODUCTS if has_more else texts.CATALOG_NO_MORE_PRODUCTS
    else:
        message_text = texts.CATALOG_NO_PRODUCTS

    await update_or_send_message(event=callback, text=message_text, reply_markup=keyboard)


async def _send_products_batch(
        event: Union[CallbackQuery, Message],
        products: list,
        offset: int = 0
):
    products_batch = products[offset:offset + config.ITEMS_PER_PAGE]

    for product in products_batch:
        caption = texts.PRODUCT_CARD_TEMPLATE.format(
            name=product.name,
            description=product.description or texts.PRODUCT_NO_DESCRIPTION,
            price=product.price
        )

        photo = FSInputFile(product.image.path) if product.image and product.image.name else None
        keyboard = await get_products_batch_keyboard(product.id)
        await update_or_send_message(event=event, photo=photo, caption=caption, force_new=True, reply_markup=keyboard)


@router.callback_query(AddToCartCallback.filter(F.quantity.is_(None)))
async def ask_for_quantity(callback: CallbackQuery, callback_data: AddToCartCallback, state: FSMContext):
    product = await sync_to_async(Product.objects.get)(id=callback_data.product_id)

    await state.update_data(product_id=product.id)
    await state.set_state(CartStates.waiting_for_quantity)

    await update_or_send_message(
        event=callback,
        text=texts.CART_ENTER_QUANTITY,
        reply_markup=None
    )


@router.message(CartStates.waiting_for_quantity)
async def process_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        await message.answer(texts.CART_INVALID_QUANTITY_MESSAGE)
        return

    data = await state.get_data()
    product_id = data.get('product_id')

    product = await sync_to_async(Product.objects.select_related('subcategory__category').get)(id=product_id)
    category_id_for_back = product.subcategory.category.id

    total_price = quantity * product.price
    keyboard = await get_confirm_quantity_keyboard(product_id, quantity, category_id_for_back)
    await message.answer(
        texts.CONFIRM_ADD_TO_CART_MESSAGE.format(
            quantity=quantity,
            product_name=product.name,
            total_price=f"{total_price:.2f}"
        ),
        reply_markup=keyboard
    )


@sync_to_async
def _perform_atomic_cart_update(tg_user, product_id, quantity):
    with transaction.atomic():
        product_obj = Product.objects.get(id=product_id)
        cart_item, created = Cart.objects.get_or_create(
            user=tg_user,
            product=product_obj,
            defaults={'quantity': quantity}
        )
        cart_item.quantity += quantity
        cart_item.save()


@router.callback_query(AddToCartCallback.filter(F.quantity.is_not(None)))
async def confirm_add_to_cart(callback: CallbackQuery, callback_data: AddToCartCallback, state: FSMContext,
                              tg_user: TelegramUser):
    await  _perform_atomic_cart_update(tg_user, callback_data.product_id, callback_data.quantity)

    await update_or_send_message(
        event=callback,
        text=texts.CART_PRODUCT_ADDED_SUCCESSFULLY,
        reply_markup=None
    )

    await state.clear()
    await show_cart(callback, state, tg_user)
