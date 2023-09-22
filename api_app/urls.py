from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    BannersApiView,
    CatalogApiView,
    ProductApiView,
    ProfileApiView,
    LimitedProductsApiView,
    PopularProductsApiView,
    ProductCategoryApiView,
    ProductReviewApiView,
    SalesProductsApiView,
    UpdatePasswordApiView,
    signUp,
    signOut,
    signIn,
    avatar,
    payment,
    TagApiView,
    OrdersApiView,
    OrderDetailApiView,
    CartDetailView,
)

app_name = "api_app"

urlpatterns = [
    path("sign-in", signIn),
    path("sign-up", signUp),
    path("sign-out", LogoutView.as_view(), name="logout"),
    path("banners", BannersApiView.as_view(), name="banners"),
    path("catalog", CatalogApiView.as_view(), name="catalog"),
    path("categories", ProductCategoryApiView.as_view(), name="categories"),
    path("products/limited", LimitedProductsApiView.as_view(), name="limited"),
    path("sales", SalesProductsApiView.as_view(), name="sales"),
    path("products/popular", PopularProductsApiView.as_view(), name="popular"),
    path("product/<int:pk>", ProductApiView.as_view(), name="product"),
    path("product/<int:pk>/reviews", ProductReviewApiView.as_view(), name="review"),
    path("orders", OrdersApiView.as_view(), name="orders"),
    path("order/<int:pk>", OrderDetailApiView.as_view(), name="order_details"),
    path("profile", ProfileApiView.as_view(), name="profile"),
    path("profile/avatar", avatar, name="avatar"),
    path("profile/password", UpdatePasswordApiView.as_view(), name="update-password"),
    path("tags", TagApiView.as_view(), name="tag"),
    path("basket", CartDetailView.as_view(), name="basket"),
    path("payment/<int:id>", payment, name="payment"),
]
