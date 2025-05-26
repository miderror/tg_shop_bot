WELCOME_MESSAGE = "👋 Привет, {user_first_name}! Добро пожаловать в наш магазин!"
DEFAULT_USER_NAME = "дорогой пользователь"

SUBSCRIPTION_REQUIRED_MESSAGE = "🚨 Для использования бота, пожалуйста, подпишитесь на следующие чаты:"

SUBSCRIPTION_CHAT_BUTTON_TEXT = "👉 {chat_title}"
SUBSCRIPTION_CHECK_BUTTON = "✅ Проверить подписку"

MAIN_MENU_CATALOG_BUTTON = "📦 Каталог"
MAIN_MENU_CART_BUTTON = "🛒 Корзина"
MAIN_MENU_FAQ_BUTTON = "❓ FAQ"

CATALOG_SELECT_CATEGORY = "Выберите категорию:"
CATALOG_NO_CATEGORIES = "Пока нет категорий товаров."
CATALOG_SELECT_SUBCATEGORY = "Выберите подкатегорию:"
CATALOG_NO_SUBCATEGORIES = "Пока нет подкатегорий товаров."
CATALOG_SHOW_MORE_PRODUCTS = "⬇️ Показать еще товары? ⬇️"
CATALOG_NO_MORE_PRODUCTS = "Это все товары в данной подкатегории"
CATALOG_NO_PRODUCTS = "В этой подкатегории пока нет товаров."
ADD_TO_CART_BUTTON = "🛒 Добавить в корзину"

PRODUCT_CARD_TEMPLATE = "<b>{name}</b>\n<i>{description}</i>\nЦена: <b>{price}₽</b>"
PRODUCT_NO_DESCRIPTION = "Нет описания"

CART_ENTER_QUANTITY = "Введите желаемое количество товара. (Только целое число, например: 1, 5, 10)"
CART_INVALID_QUANTITY_MESSAGE = "Некорректное количество."
CONFIRM_ADD_TO_CART_MESSAGE = "Добавить <b>{quantity}</b> шт. товара <b>{product_name}</b> в корзину? Общая цена: <b>{total_price}₽</b>"
CART_PRODUCT_ADDED_SUCCESSFULLY = "Товар успешно добавлен. Перенаправляю в корзину..."

CART_ITEM_TEMPLATE = (
    "<b>{item_number}. {product_name}</b>\n"
    "   Количество: <code>{quantity}</code> шт.\n"
    "   Цена за шт.: <code>{price:.2f}</code>₽\n"
    "   Итого: <code>{total_item_price:.2f}</code>₽\n\n"
)

CART_SUMMARY_TEMPLATE = (
    "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
    "<b>Общая сумма к оплате: {total_cart_price:.2f}₽</b>"
)

BACK_TO_MENU_BUTTON = "↩️ В главное меню"
BACK_TO_CATEGORY = "↩️ Назад к категориям"
BACK_TO_SUBCATEGORY = "↩️ Назад к подкатегориям"

SHOW_MORE_BUTTON = "⬇️ Показать еще ⬇️"
PAGINATION_PREV_BUTTON = "⬅️"
PAGINATION_NEXT_BUTTON = "➡️"

CART_DELETE_BUTTON = "🗑️ Удалить товары"
CART_CLEAR_ALL_BUTTON = "🗑️ Очистить все"
CART_CHECKOUT_BUTTON = "✅ Оформить заказ"
CART_COMPLETE_DELETE_BUTTON = "↩️ Завершить удаление"
CART_REMOVE_ITEM_BUTTON_PREFIX = "❌ "

EMPTY_CART_MESSAGE = "🛒 Ваша корзина пуста."
CART_HEADER_MESSAGE = "🛒 <b>Ваша корзина:</b>\n\n"
CART_PROMPT_DELETE_MESSAGE = "Выберите товар, который хотите удалить из корзины:"
CART_ITEM_DELETED_MESSAGE = "Товар удален из корзины."
CART_ERROR_DELETED_MESSAGE = "Ошибка: Товар не найден или уже удален."
CART_INVALID_DELETE_DATA_MESSAGE = "Неверные данные для удаления."
CART_CLEARED_MESSAGE = "Ваша корзина полностью очищена."
CART_EMPTY_FOR_CHECKOUT_MESSAGE = "Ваша корзина пуста, нечего оформлять."

ORDER_ENTER_DELIVERY_INFO_TEXT = (
    "Начинаем оформление заказа. Пожалуйста, введите данные для доставки (ФИО, адрес, номер телефона).\n"
    "Пример: Иванов Иван Иванович\n"
    "ул. Пушкина, д.10, кв.5\n"
    "+79123456789"
)
ORDER_EMPTY_DELIVERY_INFO_MESSAGE = "Пожалуйста, введите данные для доставки."
ORDER_MISSING_DELIVERY_INFO_MESSAGE = "Не удалось найти данные доставки. Пожалуйста, попробуйте снова."
ORDER_CONFIRMATION_PROMPT = (
    "<b>Проверьте введенные данные для доставки:</b>\n\n"
    "<code>{delivery_info}</code>\n\n"
    "Все верно?"
)
CONFIRM_BUTTON_TEXT = "✅ Подтвердить"
CANCEL_BUTTON_TEXT = "❌ Отмена"

ORDER_PROCESSING_MESSAGE = "Обрабатываем ваш заказ..."
YOOKASSA_PAYMENT_DESCRIPTION = "Оплата заказа #{order_id}"
PAYMENT_BUTTON_TEXT = "Оплатить заказ"

ORDER_PAYMENT_REQUIRED_MESSAGE = (
    "Ваш заказ #{order_id} сформирован. Пожалуйста, оплатите его.\n"
    "После оплаты вы будете уведомлены. Спасибо за покупку!"
)
ORDER_CREATION_ERROR_MESSAGE = (
    "Произошла ошибка при формировании заказа или создании платежа. "
    "Пожалуйста, попробуйте позже."
)
ORDER_PAID_NOTIFICATION = (
    "🎉 Ваш заказ №{order_id} успешно оплачен! "
    "Мы начали его формировать и скоро свяжемся с вами по поводу доставки.\n"
    "Спасибо за покупку!"
)
ORDER_CANCELED_NOTIFICATION = (
    "❌ Оплата вашего заказа №{order_id} была отменена. "
    "Если это ошибка, попробуйте оформить заказ снова или свяжитесь с нами."
)

FAQ_INLINE_QUERY_PROMPT = "Введите ваш вопрос для поиска в FAQ..."
FAQ_NO_RESULTS = "По вашему запросу ничего не найдено."
FAQ_SEARCH_PROMPT_MESSAGE = (
    "Чтобы найти ответ на вопрос, просто начните вводить\n"
    "@наш_бот ваш_запрос\n"
    "в любом чате или здесь."
)
FAQ_TRY_BUTTON_TEXT = "Попробовать"
FAQ_QUESTION_ANSWER_TEMPLATE = "<b>Вопрос:</b> {question}\n\n<b>Ответ:</b> {answer}"
