"""Views For API"""
import logging
from src.serializers import (
    RegistrationSerializer,
    MyTokenObtainPairSerializer,
    RequestsSerializer,
    MyTokenLogoutSerializer,
    InvoiceSerializer,
)
from src.models import Request, CustomUser, Invoice
from src.use_cases import get_id_by_name, get_customer_billings_by_id
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger(__name__)


class RegistrationView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=RegistrationSerializer,
        responses={"200": "Ok Request", "400": "Bad Request", "403": "User Exists"},
        operation_description="For client required fields are username, phone_number & password.\n\n"
        "For master required fields are username and password.",
    )
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            logger.debug(msg="ACCEPT REGISTRATIONS")
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        logger.debug(msg="DECLINED REGISTRATIONS")
        return Response(data=serializer.errors, status=status.HTTP_403_FORBIDDEN)


class MyTokenLoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    @swagger_auto_schema(
        request_body=serializer_class,
        operation_description="To authenticate client required fields required fields:"
        " \n- phone_number \n- password.\n\n"
        "To authenticate master(admin) required fields: \n- username \n- password.",
    )
    def post(self, request, *args, **kwargs):
        return super(MyTokenLoginView, self).post(request, *args, **kwargs)


class MyTokenLogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=MyTokenLogoutSerializer,
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="Enter refresh token to logout",
    )
    def post(self, request, *args, **kwargs):
        serializer = MyTokenLogoutSerializer(data=request.data)
        serializer.is_valid()
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestsAPISet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = RequestsSerializer
    queryset = Request.objects.all()
    http_method_names = ["get", "post", "put", "delete"]

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="Returns list of personal requests",
    )
    def list(self, request, *args, **kwargs):
        if request.user.role == CustomUser.Roles.CUSTOMER:
            id_ = get_id_by_name(request.user.username)
            self.queryset = self.queryset.filter(customer_id=id_).all()
            logger.debug(msg="role is for customer")
        queryset = self.filter_queryset(self.queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        logger.debug(msg="no enough page")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="Create new customer(client) request",
    )
    def create(self, request, *args, **kwargs):
        id_ = get_id_by_name(request.user.username)
        data = request.data
        data.setdefault("customer", id_)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        logger.debug(msg="request created")
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="Updates request info",
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        id_ = get_id_by_name(request.user.username)
        data = request.data
        data.setdefault("customer", id_)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        logger.debug(msg="request updated")

        return Response(serializer.data)

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="Remove client request",
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if (
            request.user.role == CustomUser.Roles.CUSTOMER
            and instance.status == Request.Statuses.PROCESS
        ):
            return Response({"Attention": "Non completed request cannot be remove!"})

        self.perform_destroy(instance)
        logger.debug(msg="request removed")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="Remove client request",
    )
    @action(detail=False, url_path="billings")
    def customer_billings(self, request):
        id_ = get_id_by_name(request.user.username)
        queryset = get_customer_billings_by_id(id_)
        queries = self.filter_queryset(queryset)
        page = self.paginate_queryset(queries)
        if page is not None:
            serializer = InvoiceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        logger.debug("no enough page")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="ADMIN(MASTER)ONLY!\nReturn all customer requests by username",
    )
    @action(
        detail=False,
        url_path=r"customer_filter/(?P<username>[^/]+)",
        permission_classes=[
            IsAdminUser,
        ],
    )
    def filter_requests_by_customer(self, request, username):
        id_ = get_id_by_name(username)
        queryset = self.queryset.filter(customer_id=id_).all()
        queries = self.filter_queryset(queryset)
        page = self.paginate_queryset(queries)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        logger.debug("no enough page")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="ADMIN(MASTER)ONLY!\nReturn all customer requests by word in problem description",
    )
    @action(
        detail=False,
        url_path="requests_by_problem/(?P<problem_description>[^/]+)",
        permission_classes=[
            IsAdminUser,
        ],
    )
    def filter_requests_by_problem(self, request, problem_description):
        queryset = self.queryset.filter(
            problem_description__contains=problem_description
        )
        queries = self.filter_queryset(queryset)
        page = self.paginate_queryset(queries)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        logger.debug("no enough page")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="ADMIN(MASTER)ONLY!\nReturn all customer requests by giving status and device model",
    )
    @action(
        detail=False,
        url_path="requests_by_status&model/(?P<model>[^/]+)/(?P<status>[^/]+)",
        permission_classes=[
            IsAdminUser,
        ],
    )
    def filter_requests_by_status_model(self, request, *args, **kwargs):
        model, status = kwargs.values()
        queryset = self.queryset.filter(Q(status=status) & Q(phone_model=model)).all()
        queries = self.filter_queryset(queryset)
        page = self.paginate_queryset(queries)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        logger.debug("no enough page")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class InvoiceAPISet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()
    http_method_names = ["get", "post", "put", "delete"]

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="ADMIN(MASTER)ONLY!\nList all requests bills",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="ADMIN(MASTER)ONLY!\nCreate new bill for work",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="ADMIN(MASTER)ONLY!\nUpdate price and status of work",
    )
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

    @swagger_auto_schema(
        responses={"200": "Ok Request", "400": "Bad Request"},
        operation_description="ADMIN(MASTER)ONLY!\nDrop invoice",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
