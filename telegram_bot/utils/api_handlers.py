import json
from datetime import datetime

import texts
from aiogram.exceptions import TelegramAPIError
from aiohttp import web
from asgiref.sync import sync_to_async
from django.db import transaction, DatabaseError, IntegrityError
from django.utils import timezone
from shop_app.models import Order
from utils.excel_exporter import export_order_to_excel
from yookassa.domain.notification import WebhookNotificationFactory, WebhookNotificationEventType

_bot_instance = None


def set_bot_instance(bot):
    global _bot_instance
    _bot_instance = bot


async def _process_order_payment(order_id, payment_data, status, message_to_user):
    @sync_to_async
    def update_order_status():
        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order_id)
                if order.payment_status == status or order.yookassa_payment_id != payment_data.id:
                    return None

                order.payment_status = status
                if status == Order.STATUS_PAID:
                    order.paid_at = datetime.now(tz=timezone.get_current_timezone())
                order.save()
                return order
        except (Order.DoesNotExist, DatabaseError, IntegrityError):
            return None

    order = await update_order_status()
    if not order or not _bot_instance:
        return

    try:
        await _bot_instance.send_message(
            chat_id=payment_data.metadata['telegram_user_id'],
            text=message_to_user.format(order_id=order.id)
        )
        if status == Order.STATUS_PAID:
            await export_order_to_excel(order)
    except TelegramAPIError:
        pass


async def yookassa_webhook_handler(request):
    try:
        body = await request.json()
        notification = WebhookNotificationFactory().create(body)
        payment_data = notification.object

        if not (order_id := payment_data.metadata.get('order_id')):
            return web.Response(status=400)

        if notification.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            await _process_order_payment(
                order_id,
                payment_data,
                Order.STATUS_PAID,
                texts.ORDER_PAID_NOTIFICATION
            )
        elif notification.event == WebhookNotificationEventType.PAYOUT_CANCELED:
            await _process_order_payment(
                order_id,
                payment_data,
                Order.STATUS_CANCELED,
                texts.ORDER_CANCELED_NOTIFICATION
            )

        return web.Response(status=200)

    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")
    except Exception as e:
        return web.Response(status=500)
