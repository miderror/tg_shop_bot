import uuid

import config
from asgiref.sync import sync_to_async
from yookassa import Configuration, Payment
from yookassa.domain.request import PaymentRequest
from yookassa.domain.response import PaymentResponse


def setup_yookassa_configuration():
    Configuration.account_id = config.YOOKASSA_SHOP_ID
    Configuration.secret_key = config.YOOKASSA_SECRET_KEY


async def create_yookassa_payment(
        amount: float,
        description: str,
        order_id: int,
        telegram_user_id: int
) -> PaymentResponse:
    idempotence_key = str(uuid.uuid4())
    request = PaymentRequest({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": config.YOOKASSA_RETURN_URL
        },
        "capture": True,
        "description": description,
        "metadata": {
            "order_id": order_id,
            "telegram_user_id": telegram_user_id
        }
    })

    yookassa_payment: PaymentResponse = await sync_to_async(Payment.create)(request, idempotence_key)
    return yookassa_payment
