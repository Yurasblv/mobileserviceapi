"""Module contain requests to database"""
from src.models import Request, CustomUser, Invoice
from rest_framework import serializers
from django.db.models import Q


def check_exist_user_by_username(username: str):
    """Method return bool value of by username existing user"""
    user = CustomUser.objects.filter(username=username).exists()
    if user is False:
        return user
    raise serializers.ValidationError("This username was registered.")


def check_exist_user_by_number_username(username: str, phone_number: str):
    """Method return bool value of by username  and phone number existing user"""
    user = CustomUser.objects.filter(
        Q(phone_number=phone_number) & Q(username=username)
    ).exists()
    if user is False:
        return user
    raise serializers.ValidationError("This customer was registered.")


def check_username(username: str):
    """Method return query by username"""
    try:
        return CustomUser.objects.get(username=username).username
    except CustomUser.DoesNotExist:
        raise serializers.ValidationError("This user not found")


def get_query_by_username(username: str):
    """Return query of user by username"""
    try:
        return CustomUser.objects.filter(username=username).all()
    except CustomUser.DoesNotExist:
        raise serializers.ValidationError("This user not found")


def get_id_by_name(name: str):
    """Method to extract id of user by username"""
    return CustomUser.objects.get(username=name).id


def req_status_by_id(id_: int):
    """Method to extract status of request by id field"""
    return Request.objects.get(id=id_).status


def get_username_by_phone_number(phone_number: str):
    """Method to extract username of user by phone field"""
    try:
        return CustomUser.objects.get(phone_number=phone_number).username
    except CustomUser.DoesNotExist:
        raise serializers.ValidationError("This user not found")


def get_customer_billings_by_id(id_: int):
    """Return all invoices for customer by its id"""
    return Invoice.objects.filter(request__customer_id=id_).all()
