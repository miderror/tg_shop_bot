import config
import texts
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_data import CategoryCallback, SubcategoryCallback, ProductCallback, BackCallback, AddToCartCallback


async def get_subscription_keyboard(bot: Bot, chat_ids_to_display: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for chat_id in chat_ids_to_display:
        try:
            chat = await bot.get_chat(chat_id)
            if chat.title and chat.invite_link:
                builder.row(InlineKeyboardButton(
                    text=texts.SUBSCRIPTION_CHAT_BUTTON_TEXT.format(chat_title=chat.title),
                    url=chat.invite_link)
                )
        except Exception as e:
            print("error ", e)
    builder.row(
        InlineKeyboardButton(text=texts.SUBSCRIPTION_CHECK_BUTTON, callback_data=BackCallback(to="main_menu").pack()))
    return builder.as_markup()


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=texts.MAIN_MENU_CATALOG_BUTTON, callback_data=CategoryCallback().pack()))
    builder.row(InlineKeyboardButton(text=texts.MAIN_MENU_CART_BUTTON, callback_data=BackCallback(to="cart").pack()))
    builder.row(InlineKeyboardButton(text=texts.MAIN_MENU_FAQ_BUTTON, callback_data=BackCallback(to="faq").pack()))
    return builder.as_markup()


async def get_categories_keyboard(categories: list, page: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    start_index = page * config.ITEMS_PER_PAGE
    end_index = start_index + config.ITEMS_PER_PAGE

    current_page_categories = categories[start_index:end_index]

    for category in current_page_categories:
        builder.row(InlineKeyboardButton(
            text=category.name,
            callback_data=SubcategoryCallback(category_id=category.id).pack()
        ))

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(
            text=texts.PAGINATION_PREV_BUTTON,
            callback_data=CategoryCallback(page=page - 1).pack()
        ))
    if end_index < len(categories):
        nav_row.append(InlineKeyboardButton(
            text=texts.PAGINATION_NEXT_BUTTON,
            callback_data=CategoryCallback(page=page + 1).pack()
        ))
    if nav_row:
        builder.row(*nav_row)

    builder.row(InlineKeyboardButton(text=texts.BACK_TO_MENU_BUTTON, callback_data=BackCallback(to="main_menu").pack()))

    return builder.as_markup()


async def get_subcategories_keyboard(category_id: int, subcategories: list, page: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    start_index = page * config.ITEMS_PER_PAGE
    end_index = start_index + config.ITEMS_PER_PAGE

    current_page_subcategories = subcategories[start_index:end_index]

    for subcategory in current_page_subcategories:
        builder.row(InlineKeyboardButton(
            text=subcategory.name,
            callback_data=ProductCallback(subcategory_id=subcategory.id).pack()
        ))

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(
            text=texts.PAGINATION_PREV_BUTTON,
            callback_data=SubcategoryCallback(category_id=category_id, page=page - 1).pack()
        ))
    if end_index < len(subcategories):
        nav_row.append(InlineKeyboardButton(
            text=texts.PAGINATION_NEXT_BUTTON,
            callback_data=SubcategoryCallback(category_id=category_id, page=page + 1).pack()
        ))
    if nav_row:
        builder.row(*nav_row)

    builder.row(InlineKeyboardButton(text=texts.BACK_TO_CATEGORY, callback_data=CategoryCallback().pack()))

    return builder.as_markup()


async def get_products_keyboard(
        subcategory_id: int,
        products: list,
        offset: int = 0,
        category_id_for_back: int = 0
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    has_more = offset + config.ITEMS_PER_PAGE < len(products)

    if has_more:
        builder.row(InlineKeyboardButton(
            text=texts.SHOW_MORE_BUTTON,
            callback_data=ProductCallback(
                subcategory_id=subcategory_id,
                offset=offset + config.ITEMS_PER_PAGE
            ).pack()
        ))

    builder.row(InlineKeyboardButton(
        text=texts.BACK_TO_SUBCATEGORY,
        callback_data=SubcategoryCallback(
            category_id=category_id_for_back
        ).pack()
    ))

    return builder.as_markup()


async def get_products_batch_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=texts.ADD_TO_CART_BUTTON,
        callback_data=AddToCartCallback(product_id=product_id).pack()
    ))
    return builder.as_markup()


async def get_confirm_quantity_keyboard(product_id: int, quantity: int,
                                        category_id_for_back: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=texts.CONFIRM_BUTTON_TEXT,
            callback_data=AddToCartCallback(product_id=product_id, quantity=quantity).pack()
        ),
        InlineKeyboardButton(
            text=texts.CANCEL_BUTTON_TEXT,
            callback_data=SubcategoryCallback(
                category_id=category_id_for_back
            ).pack()
        )
    )
    return builder.as_markup()


def back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=texts.BACK_TO_MENU_BUTTON, callback_data=BackCallback(to="main_menu").pack()))
    return builder.as_markup()
