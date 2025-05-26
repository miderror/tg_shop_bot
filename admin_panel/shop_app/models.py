from django.core.validators import MinValueValidator
from django.db import models


class TelegramUser(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True, verbose_name="Telegram ID")
    first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя")
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Фамилия")
    username = models.CharField(max_length=255, blank=True, null=True, verbose_name="Username")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    class Meta:
        verbose_name = "Пользователь Telegram"
        verbose_name_plural = "Пользователи Telegram"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''} | @{self.username or 'отсутствует'} | id: {self.id}"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название категории")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories',
                                 verbose_name="Категория")
    name = models.CharField(max_length=255, verbose_name="Название подкатегории")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        unique_together = ('category', 'name')
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Product(models.Model):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='products',
                                    verbose_name="Подкатегория")
    name = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)],
                                verbose_name="Цена")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Изображение товара")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name']

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        ordering = ['-user']

    def __str__(self):
        return f"Пользователь {self.user.id} - {self.product.name} ({self.quantity} шт.)"


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_CANCELED = 'canceled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает оплаты'),
        (STATUS_PAID, 'Оплачен'),
        (STATUS_CANCELED, 'Отменен'),
    ]

    user = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, null=True, related_name='orders',
                             verbose_name="Пользователь Telegram")
    delivery_info = models.TextField(verbose_name="Данные доставки")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")

    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING,
                                      verbose_name="Статус оплаты")
    yookassa_payment_id = models.CharField(max_length=255, blank=True, null=True, unique=True,
                                           verbose_name="ID платежа ЮKassa")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата оплаты")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username or self.user.id} ({self.get_payment_status_display()})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="Товар")

    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена на момент покупки")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.product.name if self.product else 'Удаленный товар'} ({self.quantity} шт.) в заказе #{self.order.id}"


class FAQ(models.Model):
    question = models.CharField(max_length=500, unique=True, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    keywords = models.CharField(max_length=500, blank=True, null=True,
                                verbose_name="Ключевые слова для поиска (через запятую)")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок отображения")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
        ordering = ['order', 'question']

    def __str__(self):
        return self.question


class Mailing(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_SENDING = 'sending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик'),
        (STATUS_SENDING, 'Отправляется'),
        (STATUS_SENT, 'Отправлено'),
        (STATUS_FAILED, 'Ошибка отправки'),
    ]

    message_text = models.TextField(verbose_name="Текст сообщения")
    photo = models.ImageField(upload_to='mailing_photos/', blank=True, null=True,
                              verbose_name="Изображение для рассылки")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT, verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата отправки")
    total_users = models.PositiveIntegerField(default=0, verbose_name="Всего пользователей")
    successful_sends = models.PositiveIntegerField(default=0, verbose_name="Успешных отправок")
    failed_sends = models.PositiveIntegerField(default=0, verbose_name="Неудачных отправок")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Рассылка от {self.created_at.strftime('%Y-%m-%d %H:%M')} ({self.get_status_display()})"
