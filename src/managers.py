"""Module needed to create for custom user module and setting authentication
 and registration solutions"""
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import ValidationError


class CustomUserManager(BaseUserManager):
    """Base class rewriting"""

    def _create_user(self, username, password, **extra_fields):
        """Route for continue superuser creation"""
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, username, phone_number, password, **extra_fields):
        """Route for continue default user"""
        extra_fields.setdefault("role", "CUSTOMER")
        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        """Route for continue superuser"""
        extra_fields.setdefault("role", "MASTER")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValidationError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValidationError(_("Superuser must have is_superuser=True."))
        return self._create_user(username=username, password=password, **extra_fields)
