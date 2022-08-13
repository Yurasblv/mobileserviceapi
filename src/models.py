"""Models module"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from src.managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Refactoring base django user module with separated roles for customer and admin.
    Also in views representing customising authentication with simple_jwt token
    """

    class Roles(models.TextChoices):
        CUSTOMER = "CUSTOMER", _("CUSTOMER")
        MASTER = "MASTER", _("MASTER")

    role = models.CharField(choices=Roles.choices, default=Roles.CUSTOMER, max_length=8)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    password = models.CharField(max_length=255, null=False)
    username = models.CharField(max_length=255, unique=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now)
    first_name = None
    last_name = None
    email = None

    USERNAME_FIELD = "username"
    EMAIL_FIELD = None

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        if len(self.username) != 0:
            return f"{self.role} := {self.username}"
        return f"{self.role} := {self.phone_number}"


class Request(models.Model):
    """Request model"""

    class Statuses(models.TextChoices):
        PROCESS = "PROCESS", _("PROCESS")
        DONE = "DONE", _("DONE")

    status = models.CharField(
        choices=Statuses.choices, default=Statuses.PROCESS, max_length=30
    )
    phone_model = models.CharField(max_length=10)
    problem_description = models.TextField(max_length=255)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class Invoice(models.Model):
    """Invoice model"""

    class Statuses(models.TextChoices):
        UNPAID = "UNPAID", _("UNPAID")
        PAID = "PAID", _("PAID")

    price = models.FloatField(editable=True)
    status = models.CharField(
        choices=Statuses.choices, default=Statuses.UNPAID, max_length=30
    )
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
