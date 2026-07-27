# app_users/services.py

import stripe
from django.conf import settings

from app_materials.models import Course, Lesson

from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(course: Course | None, lesson: Lesson | None, name: str, description: str | None) -> str:
    """
    Создаёт продукт в Stripe и возвращает его ID.
    """
    product = stripe.Product.create(
        name=name,
        description=description,
    )
    return product.id


def create_stripe_price(product_id: str, amount: int) -> str:
    """
    Создаёт цену в Stripe (amount – в копейках/центах *100).
    Возвращает Price ID.
    """
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount,
        currency="rub",  # или USD.
    )
    return price.id


def create_stripe_checkout_session(price_id: str, user_email: str, payment_id: int) -> str:
    """
    Создаёт Checkout Session и возвращает URL оплаты.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            },
        ],
        mode="payment",
        success_url=f"http://127.0.0.1:8000/app_users/payments/{payment_id}/success/",
        cancel_url=f"http://127.0.0.1:8000/app_users/payments/{payment_id}/cancel/",
        customer_email=user_email,
        metadata={
            "payment_id": str(payment_id),
        },
    )
    return session.url  # type: ignore[return-value]
