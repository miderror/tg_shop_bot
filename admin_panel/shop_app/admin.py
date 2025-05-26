import asyncio
import os
import threading

from aiogram import Bot
from aiogram.types import FSInputFile
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone

from .models import TelegramUser, Category, Subcategory, Product, Cart, Order, OrderItem, FAQ, Mailing


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'username', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'username', 'id')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order',)
    list_editable = ('order',)
    search_fields = ('name',)
    list_per_page = 20


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order',)
    list_editable = ('order',)
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    list_per_page = 20

    autocomplete_fields = ['category']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategory', 'price', 'created_at')
    list_editable = ('price',)
    search_fields = ('name', 'description', 'subcategory__name', 'subcategory__category__name')
    list_filter = ('subcategory__category', 'subcategory',)
    list_per_page = 20

    fields = (
        'name',
        'subcategory',
        'description',
        'price',
        'image',
    )
    readonly_fields = ('created_at', 'updated_at',)

    autocomplete_fields = ['subcategory']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user__username', 'user__first_name', 'product__name')
    list_filter = ('user',)
    list_editable = ('quantity',)
    ordering = ['user', 'product__name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price_at_purchase',)
    readonly_fields = ('price_at_purchase',)
    autocomplete_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'total_amount',
        'payment_status',
        'yookassa_payment_id',
        'created_at',
        'paid_at'
    )
    list_filter = ('payment_status', 'created_at', 'paid_at')
    search_fields = ('user__username', 'user__id', 'id', 'yookassa_payment_id')
    readonly_fields = ('created_at', 'paid_at', 'total_amount', 'yookassa_payment_id')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'total_amount', 'payment_status', 'yookassa_payment_id', 'created_at', 'paid_at')
        }),
        ('Информация о доставке', {
            'fields': ('delivery_info',),
            'classes': ('collapse',),
        }),
    )

    inlines = [OrderItemInline]
    autocomplete_fields = ['user']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('question', 'answer', 'keywords')
    list_filter = ('is_active',)
    ordering = ('order',)
    fields = ('question', 'answer', 'keywords', 'order', 'is_active')
    list_per_page = 20


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'status', 'total_users', 'successful_sends', 'failed_sends',
        'created_at', 'sent_at'
    )
    list_filter = ('status', 'created_at',)
    search_fields = ('message_text',)
    readonly_fields = ('status', 'created_at', 'sent_at', 'total_users', 'successful_sends', 'failed_sends',)
    fields = ('message_text', 'photo')

    change_form_template = "admin/mailing_change_form.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<path:object_id>/send_mailing/', self.admin_site.admin_view(self.send_mailing_view),
                 name='send_mailing'),
        ]
        return my_urls + urls

    def send_mailing_view(self, request, object_id):
        mailing = self.get_object(request, object_id)

        if mailing.status != Mailing.STATUS_DRAFT:
            return redirect('admin:shop_app_mailing_change', object_id=object_id)

        if request.method != 'POST':
            context = self.admin_site.each_context(request)
            context['mailing'] = mailing
            context['opts'] = self.model._meta
            context['has_view_permission'] = self.has_view_permission(request, obj=mailing)
            context['has_add_permission'] = self.has_add_permission(request)
            context['has_change_permission'] = self.has_change_permission(request, obj=mailing)
            context['has_delete_permission'] = self.has_delete_permission(request, obj=mailing)

            return TemplateResponse(request, "admin/send_mailing_confirm.html", context)

        mailing.status = Mailing.STATUS_SENDING
        mailing.sent_at = timezone.now()
        mailing.save()

        mailing_thread = threading.Thread(target=self._start_mailing_thread, args=(mailing.id,))
        mailing_thread.daemon = True
        mailing_thread.start()

        self.message_user(request,
                          f"Рассылка '{mailing}' запущена в фоновом режиме. Статус будет обновлен по мере отправки.")
        return redirect('admin:shop_app_mailing_change', object_id=object_id)

    def _start_mailing_thread(self, mailing_id):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._perform_mailing(mailing_id))
        except Exception as e:
            pass

    async def _perform_mailing(self, mailing_id):
        mailing = await sync_to_async(Mailing.objects.get)(id=mailing_id)

        all_users = await sync_to_async(list)(TelegramUser.objects.all())
        mailing.total_users = len(all_users)
        await sync_to_async(mailing.save)()

        successful_count = 0
        failed_count = 0

        async with Bot(token=settings.BOT_TOKEN) as bot:
            if not bot:
                mailing.status = Mailing.STATUS_FAILED
                await sync_to_async(mailing.save)()
                return

            for user in all_users:
                try:
                    if mailing.photo:
                        photo_path = mailing.photo.path
                        if photo_path and os.path.exists(photo_path):
                            await bot.send_photo(
                                chat_id=user.id,
                                photo=FSInputFile(photo_path),
                                caption=mailing.message_text,
                                parse_mode="HTML"
                            )
                        else:
                            await bot.send_message(
                                chat_id=user.id,
                                text=mailing.message_text,
                                parse_mode="HTML"
                            )
                    else:
                        await bot.send_message(
                            chat_id=user.id,
                            text=mailing.message_text,
                            parse_mode="HTML"
                        )
                    successful_count += 1
                    await asyncio.sleep(0.05)
                except Exception as e:
                    failed_count += 1

        mailing.successful_sends = successful_count
        mailing.failed_sends = failed_count
        if failed_count == mailing.total_users:
            mailing.status = Mailing.STATUS_FAILED
        elif successful_count > 0:
            mailing.status = Mailing.STATUS_SENT
        else:
            mailing.status = Mailing.STATUS_FAILED

        await sync_to_async(mailing.save)()
