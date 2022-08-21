"""Module needed to create for custom user module and setting authentication
 and registration solutions"""
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import ValidationError


class UserManager(BaseUserManager):
    """Base class rewriting"""

    def create_user(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("role", "MASTER")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone_number=phone_number, password=password, **extra_fields)
