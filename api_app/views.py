import datetime
import random
from urllib.parse import urlparse

import requests
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.http import HttpResponse, HttpRequest
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    UpdateAPIView,
    CreateAPIView,
    RetrieveAPIView,
)
from django.shortcuts import render, redirect
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
)
import json
from django.db.models import Avg, Count
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from cart_app.cart import Cart
from shop_app.models import (
    Product,
    ProductCategory,
    Tag,
    SubCategory,
    SubCategoryImage,
    ProductImage,
    Review,
    Order,
    Sale,
    OrderProductCount,
)
from profile_app.models import Profile, Avatar, profile_avatar_dir_path
from .serializers import (
    ProductSerializer,
    ProfileSerializer,
    ProductCategorySerializer,
    UpdatePasswordSerializer,
    TagsSerializer,
    SubcategorySerializer,
    ReviewsSerializer,
    OrdersSerializer,
    SalesSerializer,
    SetProductsSerializer,
)
from .pagination import PaginationClass
import re
from datetime import date


class BannersApiView(APIView):
    """Представление для получения баннера сайта."""

    def get(self, request: Request) -> Response:
        products = Product.objects.all()
        serialized = SetProductsSerializer(products, many=True)
        return Response(random.choices(serialized.data, k=2))


class LimitedProductsApiView(APIView):
    """Представление для получения списка лимитированных товаров."""

    def get(self, request: Request) -> Response:
        products = Product.objects.filter(count__lte=12)
        serialized = SetProductsSerializer(products, many=True)
        return Response(serialized.data)


class PopularProductsApiView(APIView):
    """Представление для получения списка популярных товаров."""

    def get(self, request: Request) -> Response:
        products = Product.objects.annotate(count_review=Count("review")).filter(
            count_review__gte=2
        )
        serialized = SetProductsSerializer(products, many=True)
        return Response(serialized.data)


class CatalogApiView(ListAPIView):
    """Представление для получения каталога товаров."""

    serializer_class = SetProductsSerializer
    pagination_class = PaginationClass

    def parse_catalog(self, data):
        pattern = "/catalog/(.)/"
        num = re.findall(pattern, str(data))
        return num

    def get_queryset(self):
        queryset = Product.objects.annotate(
            reviews=Count("review"), rating=Avg("review__rate")
        )
        if self.request.query_params:
            name = self.request.query_params.get("filter[name]")
            if name:
                queryset = queryset.filter(title__icontains=name)

            freeDelivery = self.request.query_params.get("filter[freeDelivery]")
            if freeDelivery == "true":
                queryset = queryset.filter(freeDelivery=True)

            available = self.request.query_params.get("filter[available]")
            if available == "true":
                queryset = queryset.filter(available="true")

            # category_id = self.request.query_params.get("category")
            data = urlparse(self.request.META.get("HTTP_REFERER", ""))
            category_id = self.parse_catalog(data)

            if len(category_id) > 0:
                queryset = queryset.filter(category__id=category_id[0])

            tags = self.request.query_params.get("tags[]")
            if tags:
                queryset = queryset.filter(tags__in=list(map(int, tags)))

            sortType = self.request.query_params.get("sortType")
            sort = self.request.query_params.get("sort")

            if sort:
                sort_params = {
                    "decrating": "rating",
                    "incrating": "-rating",
                    "decprice": "price",
                    "incprice": "-price",
                    "decdate": "date",
                    "incdate": "-date",
                    "decreviews": "reviews",
                    "increviews": "-reviews",
                }[sortType + sort]
            queryset = queryset.order_by(sort_params)
        return queryset


class SalesProductsApiView(ListAPIView):
    queryset = Sale.objects.select_related("product")
    serializer_class = SalesSerializer
    pagination_class = PaginationClass


class ProductApiView(RetrieveAPIView):
    """Представление для получения товара."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "pk"


class ProductCategoryApiView(APIView):
    """Представление для получения категорий и подкатегорий товаров."""

    def get(self, request: Request) -> Response:
        queryset = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(queryset, many=True)
        return Response(list(serializer.data))


class ProductReviewApiView(APIView):
    """Представление для создания отзыва."""

    def post(self, request: Request, pk="pk") -> Response:
        product = Product.objects.get(pk=pk)
        data = request.data
        instance = request.user.profile
        new_review = Review.objects.create(
            product=product,
            author=instance,
            text=data["text"],
            rate=data["rate"],
        )
        return Response(ReviewsSerializer(new_review).data)


class ProfileApiView(APIView):
    """Представление для получения информации о пользователе."""

    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        if request.method == "GET":
            instance = request.user.profile
            serializer = ProfileSerializer(instance)
            return Response(serializer.data)

    def post(self, request: Request) -> Response:
        obj = request.user.profile
        profile = Profile.objects.get(id=obj.id)
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            full_name = serializer.data.get("fullName")
            email = serializer.data.get("email")
            phone = serializer.data.get("phone")
            profile.fullName = full_name
            profile.email = email
            profile.phone = phone
            profile.save()
            return Response(serializer.data)
        return Response(serializer.data)


class UpdatePasswordApiView(APIView):
    """Представление для изменения пароля пользователя."""

    serializer_class = UpdatePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request) -> Response:
        obj = request.user
        data = request.data
        serializer = UpdatePasswordSerializer(data=data)

        if serializer.is_valid():
            current_password = serializer.data.get("currentPassword")
            if not obj.check_password(current_password):
                return Response(
                    {"currentPassword": "wrong"},
                )

            obj.set_password(serializer.data.get("newPassword"))
            obj.save()
            return Response(serializer.data)


def avatar(request):
    if request.method == "POST":
        profile = request.user.profile
        file = request.FILES["avatar"]
        profile.avatar.src = file
        profile.avatar.save()
    return HttpResponse(status=200)


def signIn(request):
    if request.method == "POST":
        body = json.loads(request.body)
        username = body["username"]
        password = body["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)


@transaction.atomic
def signUp(request: Request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data["username"]
        name = data["name"]
        password = data["password"]

        user = User.objects.create_user(username=username, password=password)
        user.save()
        profile = Profile.objects.create(fullName=name, user_id=user.id)
        Avatar.objects.create(profile=profile, src=None, alt="default")
        return HttpResponse(status=200)


def signOut(request):
    logout(request)
    return HttpResponse(status=200)


class TagApiView(APIView):
    """Представление для получения тэгов."""

    def get(self, request: Request) -> Response:
        queryset = Tag.objects.all()
        serializer = TagsSerializer(queryset, many=True)
        return Response(serializer.data)


class OrdersApiView(APIView):
    """Представление для получения списка заказов."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Order.objects.select_related("profile").prefetch_related("products")
        serializer = OrdersSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        cart = Cart(request)
        profile = request.user.profile
        order = Order.objects.create(profile=profile)
        for item, value in cart.cart.items():
            product = Product.objects.get(id=item)

            OrderProductCount.objects.create(
                product=product, order=order, count_product=value["quantity"]
            )
            order.products.add(product)
            product.count -= value["quantity"]
            if product.count == 0:
                product.available = product.AVAILABLE_CHOICES[1][1]
            product.save()
        order.status = Order.STATUS_CHOICES[1][1]

        order.save()
        return Response({"orderId": order.id})


class OrderDetailApiView(APIView):
    """Представление для получения заказа."""

    def get(self, request, pk):
        queryset = Order.objects.get(pk=pk)
        serializer = OrdersSerializer(queryset)
        return Response(serializer.data)

    def post(self, request, pk):
        order = Order.objects.get(id=pk)
        data = self.request.data.get("paymentType")
        # if data == 'cash':
        #     return HttpResponse(status=400)

        order.save()
        return Response({"orderId": order.id})


class CartDetailView(APIView):
    """Представление для получения корзины, реализация методов get, post и delete"""

    def get_cart_items(self, cart):
        cart_items = []
        for item in cart:
            product = Product.objects.get(id=item["product_id"])
            cart_items.append(
                {
                    "id": product.id,
                    "category": product.category.id,
                    "price": float(item["price"]),
                    "count": item["quantity"],
                    "date": product.date.strftime("%a %b %d %Y %H:%M:%S GMT%z (%Z)"),
                    "title": product.title,
                    "description": product.description,
                    "freeDelivery": product.freeDelivery,
                    "images": [
                        {"src": image.src.url, "alt": image.alt}
                        for image in product.images.all()
                    ],
                    "tags": [
                        {"id": tag.id, "name": tag.name} for tag in product.tags.all()
                    ],
                    "reviews": Review.objects.filter(product_id=product.pk).aggregate(
                        count_review=Count("id")
                    )["count_review"],
                    "rating": Review.objects.filter(product_id=product.id).aggregate(
                        average_rating=Avg("rate")
                    )["average_rating"],
                }
            )

        return cart_items

    def get(self, request):
        cart = Cart(request)
        cart_items = self.get_cart_items(cart)
        return Response(cart_items)

    def post(self, request):
        product_id = request.data.get("id")
        quantity = int(request.data.get("count", 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        cart = Cart(request)
        cart.add(product, quantity)
        cart_items = self.get_cart_items(cart)
        return Response(cart_items)

    def delete(self, request):
        product_id = request.data.get("id")
        quantity = request.data.get("count", 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        cart = Cart(request)
        cart.remove(product, quantity)
        cart_items = self.get_cart_items(cart)
        return Response(cart_items)


@transaction.atomic
def payment(request, id):
    body = json.loads(request.body)
    cart = Cart(request)
    order = Order.objects.get(id=id)
    order.status = Order.STATUS_CHOICES[2][1]
    date_now = date.today()
    if int(body["month"]) in [1, 3, 5, 7, 8, 10, 12]:
        last_day = 31
    elif int(body["month"]) in [2, 4, 6, 9, 11]:
        last_day = 30
    else:
        last_day = 29

    cart_date = datetime.date(int("20" + body["year"]), int(body["month"]), last_day)
    if cart_date < date_now:
        print("cart is not available")
        return HttpResponse(status=400)
    if len(body["code"]) != 3:
        return HttpResponse(status=400)

    else:
        order.save()
        cart.clear()
        return HttpResponse(status=200)
