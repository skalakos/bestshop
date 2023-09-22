from django.contrib import admin
from django.db.models import QuerySet, Min
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.db.models import Avg, Count, Sum
from django.utils.translation import gettext_lazy as _
from .models import (
    Product,
    Order,
    ProductImage,
    ProductCategory,
    CatagoryImage,
    Tag,
    SubCategory,
    SubCategoryImage,
    Review,
    Sale,
    Specification,
)


class OrderInline(admin.TabularInline):
    model = Product.orders.through
    verbose_name_plural = _("orders")
    verbose_name = _("order")


class ProductInline(admin.StackedInline):
    model = ProductImage


class TagInline(admin.TabularInline):
    model = Product.tags.through


class RatingInline(admin.TabularInline):
    model = Review


class SaleInline(admin.StackedInline):
    model = Sale


class SpecificationInline(admin.StackedInline):
    model = Specification


@admin.action(description=_("available"))
def mark_available(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(available="true")


@admin.action(description=_("not available"))
def mark_not_available(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(available="false")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = [mark_available, mark_not_available]

    inlines = [
        OrderInline,
        ProductInline,
        TagInline,
        RatingInline,
        SaleInline,
        SpecificationInline,
    ]
    readline = [RatingInline]

    list_display = (
        "pk",
        "title",
        "preview_show",
        "price",
        "description",
        "category",
        "count",
        "archived",
        "date",
        "rating",
        "reviews",
        "sale",
        "available",
        "freeDelivery",
    )
    list_display_links = "pk", "title"
    ordering = ("pk",)
    search_fields = "title", "description", "price"
    fieldsets = [
        (
            _("About product"),
            {
                "fields": (
                    "title",
                    "category",
                    "description",
                    "fullDescription",
                    "price",
                    "count",
                    "available",
                    "freeDelivery",
                )
            },
        ),
        (
            _("Extra options"),
            {
                "fields": ("archived",),
                "description": 'Field "archived" is for soft delete',
                "classes": ("collapse",),
            },
        ),
        (
            _("images"),
            {
                "fields": ("preview",),
            },
        ),
    ]

    def rating(self, obj):
        result = Review.objects.filter(product=obj).aggregate(Avg("rate"))
        return result["rate__avg"]

    def reviews(self, obj):
        result = Review.objects.filter(product=obj).aggregate(Count("product"))
        return result["product__count"]

    def sale(self, obj):
        result = Sale.objects.filter(product=obj).aggregate(Min("salePrice"))
        return result["salePrice__min"]

    def preview_show(self, obj):
        if obj.preview:
            return mark_safe("<img src='{}' width='60' />".format(obj.preview.url))
        return "None"

    preview_show.__name__ = "preview"


class ProductInline(admin.TabularInline):
    model = Order.products.through
    verbose_name_plural = _("products_in_order")
    verbose_name = _("product_in_order")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline,
    ]

    list_display = (
        "pk",
        "user_verbose",
        "createdAt",
        "status",
        "paymentType",
        "total_price",
    )

    fieldsets = [
        (
            _("About order"),
            {
                "fields": (
                    "profile",
                    "city",
                    "address",
                    "status",
                    "paymentType",
                )
            },
        )
    ]

    def get_queryset(self, request):
        return Order.objects.select_related("profile").prefetch_related("products")

    def total_price(self, obj):
        result = Order.objects.filter(id=obj.id).aggregate(
            prod_sum=Sum("products__price")
        )
        return result["prod_sum"]

    @admin.display(description=_("user_verbose"))
    def user_verbose(self, obj: Order) -> str:
        return obj.profile.fullName or obj.profile.user.username


class ProductCategoryInline(admin.TabularInline):
    model = Product
    verbose_name = _("product")
    verbose_name_plural = _("products")


class ImageCategoryInline(admin.StackedInline):
    model = CatagoryImage


class SubCategoryInline(admin.TabularInline):
    model = SubCategory


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    inlines = [
        ProductCategoryInline,
        ImageCategoryInline,
        SubCategoryInline,
    ]

    list_display = (
        "pk",
        "title",
    )
    list_display_links = (
        "pk",
        "title",
    )
    fieldsets = [
        (_("Category"), {"fields": ("title", "description")}),
    ]


class SubcategoryImageInline(admin.TabularInline):
    model = SubCategoryImage


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    inlines = [SubcategoryImageInline]

    list_display = (
        "pk",
        "title",
    )
    list_display_links = (
        "pk",
        "title",
    )


class ProductTagsInline(admin.TabularInline):
    model = Product.tags.through


@admin.register(Tag)
class ProductCategoryAdmin(admin.ModelAdmin):
    inlines = [ProductTagsInline]
    list_display = (
        "pk",
        "name",
    )
    list_display_links = (
        "pk",
        "name",
    )
    fields = ("name",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "author",
        "product",
        "label",
        "date",
        "rate",
    )
