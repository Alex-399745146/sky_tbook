# app_users/serializers.py

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Payment

User = get_user_model()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "payment_date",
            "paid_course",
            "paid_lesson",
            "amount",
            "payment_method",
        )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "avatar",
            "phone",
            "city",
        )


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "avatar",
            "phone",
            "city",
            "password",
        )

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data.get("email"),
            avatar=validated_data.get("avatar"),
            phone=validated_data.get("phone", ""),
            city=validated_data.get("city", ""),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CreatePaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            "paid_course",
            "paid_lesson",
            "amount",
            "payment_method",
        )

    def validate(self, attrs):
        has_course = attrs.get("paid_course") is not None
        has_lesson = attrs.get("paid_lesson") is not None
        if has_course == has_lesson:
            raise serializers.ValidationError("Укажите ровно один объект оплаты: paid_course или paid_lesson.")
        if attrs["amount"] <= 0:
            raise serializers.ValidationError({"amount": "Сумма должна быть больше нуля."})
        return attrs
