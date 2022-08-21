"""Views For API"""
import logging
from src.serializers import (
    RegistrationSerializer,
    RequestsSerializer,
    MyTokenLogoutSerializer,
    InvoiceSerializer,
)
from src.models import Request, User, Invoice
from rest_framework import status, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

logger = logging.getLogger(__name__)


class RegistrationView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer


class MyTokenLoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class MyTokenLogoutView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MyTokenLogoutSerializer


class RequestsAPISet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = RequestsSerializer
    queryset = Request.objects.all()
    http_method_names = ["get", "post", "put", "delete"]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = ['phone_model', 'customer', 'status']
    search_fields = ['problem_description']

    def filter_queryset(self, queryset):
        if self.request.user.role == User.Roles.MASTER:
            return super().get_queryset()
        return super().filter_queryset(
            self.queryset.filter(customer_id=self.request.user.id)
        )

    def create(self, request, *args, **kwargs):
        request.data.setdefault("customer", request.user.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        logger.debug(msg="request created")
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        request.data.setdefault("customer", request.user.id)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        logger.debug(msg="request updated")
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if (
                request.user.role == User.Roles.CUSTOMER
                and instance.status == Request.Statuses.PROCESS
        ):
            return Response({"Attention": "Non completed request cannot be remove!"})

        self.perform_destroy(instance)
        logger.debug(msg="request removed")
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvoiceAPISet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()
    http_method_names = ["get", "post", "put", "delete"]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if instance.status == Invoice.Statuses.UNPAID:
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            if getattr(instance, "_prefetched_objects_cache", None):
                instance._prefetched_objects_cache = {}
            return Response(serializer.data)
        return Response({"Attention": "Invoice was not paid\n Decline!"})
