from aiogram.filters.callback_data import CallbackData


class CategoryCallback(CallbackData, prefix="cat"):
    page: int = 0


class SubcategoryCallback(CallbackData, prefix="subcat"):
    category_id: int
    page: int = 0


class ProductCallback(CallbackData, prefix="prod"):
    subcategory_id: int
    offset: int = 0


class BackCallback(CallbackData, prefix='back'):
    to: str


class AddToCartCallback(CallbackData, prefix='add_cart'):
    product_id: int = 0
    quantity: int | None = None


class DeleteCartCallback(CallbackData, prefix='del_cart'):
    page: int = 0
    cart_item_id: int | None = None
    delete_all: bool = False


class OrderCallback(CallbackData, prefix='order'):
    is_confirm: bool = False
