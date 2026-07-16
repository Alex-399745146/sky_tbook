# app_users/serializers.py

from django.contrib.auth import get_user_model
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
        )

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
