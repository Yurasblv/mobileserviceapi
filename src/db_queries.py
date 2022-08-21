"""Module contain requests to database"""
from src.models import Request, User, Invoice
from rest_framework import serializers


def check_exist_user_by_phone_number(username):
    """Method return bool value of by username existing user"""
    user = User.objects.filter(username=username).exists()
    if user is False:
        return user
    raise serializers.ValidationError("This username was registered.")


def check_username(username):
    """Method return query by username"""
    try:
        return User.objects.get(username=username).username
    except User.DoesNotExist:
        raise serializers.ValidationError("This user not found")


def get_query_by_username(username):
    """Return query of user by username"""
    try:
        return User.objects.filter(username=username).all()
    except User.DoesNotExist:
        raise serializers.ValidationError("This user not found")


def req_status_by_id(request_id):
    """Method to extract status of request by id field"""
    return Request.objects.get(id=request_id).status


def get_username_by_phone_number(phone_number):
    """Method to extract username of user by phone field"""
    try:
        return User.objects.get(phone_number=phone_number).username
    except User.DoesNotExist:
        raise serializers.ValidationError("This user not found")


def get_customer_billings_by_id(customer_id_: int):
    """Return all invoices for customer by its id"""
    return Invoice.objects.filter(request__customer_id=customer_id_)
