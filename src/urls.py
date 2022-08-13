"""Router for endpoints"""
from django.urls import path, include
from src import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("cabinet", views.RequestsAPISet, basename="title")
router.register("billing", views.InvoiceAPISet, basename="billing")

urlpatterns = [
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path("login/", views.MyTokenLoginView.as_view(), name="login"),
    path("logout/", views.MyTokenLogoutView.as_view(), name="logout"),
    path("", include(router.urls)),
]
