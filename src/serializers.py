"""Serializing module for model instances"""
import re
from src.models import User, Request, Invoice
from src.db_queries import (
    req_status_by_id,
)
from django.utils.text import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class RegistrationSerializer(serializers.ModelSerializer):
    """Serialize Client and Admin instances"""

    phone_number = serializers.CharField(min_length=2, max_length=30, required=True)
    password = serializers.CharField(
        min_length=4,
        max_length=30,
    )

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}
        swagger_schema_fields = {
            "example": {
                "phone_number": "+380992228811",
                "password": "123456",
            },
        }

    def validate(self, attrs):
        if bool(re.search(r"^\+38\d{10}$", attrs["phone_number"])) is True:
            return attrs
        if "phone_number" not in attrs.keys():
            raise serializers.ValidationError("Not found credentials for registration")
        else:
            raise serializers.ValidationError("Incorrect phone number")

    def create(self, validated_data):
        return self.Meta.model.objects.create_user(**validated_data)


class MyTokenLogoutSerializer(serializers.Serializer):
    """Remove refresh token for logout"""

    refresh = serializers.CharField(required=True)
    default_error_messages = {"bad_token": _("Token is invalid or expired")}

    def validate(self, attrs):
        """Validate token with incoming"""
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        """Add token to blacklist for logout"""
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("bad_token")


class RequestsSerializer(serializers.ModelSerializer):
    """Serializer for customer requests"""

    class Meta:
        model = Request
        fields = "__all__"
        swagger_schema_fields = {
            "example": {
                "phone_model": "regular_customer",
                "problem_description": "+380992228811",
            },
        }


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for coming invoices"""

    class Meta:
        model = Invoice
        fields = "__all__"
        swagger_schema_fields = {
            "example": {
                "price": 101.23,
                "status": "UNPAID",
                "request": 3,
            },
        }

    def validate(self, attrs):
        """Function that set rule for not done requests Ex: If request still in working , it will raise Exception"""
        if req_status_by_id(request_id=self.initial_data["request"]) == Request.Statuses.PROCESS:
            raise serializers.ValidationError("This request is being developing")
        else:
            return attrs
