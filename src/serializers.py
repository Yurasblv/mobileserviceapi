"""Serializing module for model instances"""
import re
from src.models import CustomUser, Request, Invoice
from src.use_cases import (
    req_status_by_id,
    get_username_by_phone_number,
    check_exist_user_by_username,
    check_exist_user_by_number_username,
    check_username,
)
from django.utils.text import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    PasswordField,
)


class RegistrationSerializer(serializers.ModelSerializer):
    """Serialize Client and Admin instances"""

    password = serializers.CharField(
        min_length=4,
        max_length=30,
    )
    username = serializers.CharField(min_length=4, max_length=30, required=False)
    phone_number = serializers.CharField(min_length=2, max_length=30, required=False)

    class Meta:
        model = CustomUser
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}
        swagger_schema_fields = {
            "example": {
                "username": "regular_customer",
                "phone_number": "+380992228811",
                "password": "123456",
            },
        }

    def validate(self, attrs):
        if "phone_number" in attrs.keys() and "username" in attrs.keys():
            if bool(re.search(r"^\+38\d{10}$", attrs["phone_number"])) is True:
                return self._client(attrs)
            else:
                raise serializers.ValidationError("Incorrect phone number")
        if "phone_number" not in attrs.keys() and "username" in attrs.keys():
            return self._master(attrs)
        if "phone_number" not in attrs.keys() and "username" not in attrs.keys():
            raise serializers.ValidationError("Not found credentials for registration")

    def _client(self, attrs):
        check_exist_user_by_number_username(attrs["username"], attrs["phone_number"])
        check_exist_user_by_username(attrs["username"])
        return self.Meta.model.objects.create_user(
            attrs["username"], attrs["phone_number"], attrs["password"]
        )

    def _master(self, attrs):
        if check_exist_user_by_username(attrs["username"]):
            return self.Meta.model.objects.create_superuser(
                attrs["username"], attrs["password"]
            )


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serialize token for authentication"""

    def __init__(self, *args, **kwargs):
        super(TokenObtainPairSerializer, self).__init__(*args, **kwargs)
        self.fields["username"] = serializers.CharField(
            min_length=4, max_length=30, required=False
        )
        self.fields["phone_number"] = serializers.CharField(
            min_length=2, max_length=30, required=False
        )
        self.fields["password"] = PasswordField()

    def validate(self, attrs):
        """Separate validation for different incoming data"""
        if "phone_number" in attrs.keys() and "username" not in attrs.keys():
            return self._client(attrs)
        if "phone_number" not in attrs.keys() and "username" in attrs.keys():
            return self._master(attrs)
        if "phone_number" not in attrs.keys() and "username" not in attrs.keys():
            raise serializers.ValidationError("Not found credentials for login")

    def _client(self, attrs):
        """Continue validation func for customer"""
        username = get_username_by_phone_number(attrs["phone_number"])
        new_attrs = {"username": username, "password": attrs["password"]}
        return super().validate(new_attrs)

    def _master(self, attrs):
        """Continue validation func for master(admin)"""
        username = check_username(attrs["username"])
        new_attrs = {"username": username, "password": attrs["password"]}
        return super().validate(new_attrs)


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

    def create(self, raise_exception=False):
        """Function that set rule for not done requests Ex: If request still in working , it will raise Exception"""
        id_ = self.initial_data["request"]
        if req_status_by_id(id_=id_) == Request.Statuses.PROCESS:
            raise serializers.ValidationError("This request is being developing")
        else:
            return super(InvoiceSerializer, self).create(self.validated_data)
