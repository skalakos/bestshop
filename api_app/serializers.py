from django.contrib.auth.models import User
from requests import request
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.db.models import Avg, Count, Sum

from cart_app.cart import Cart
from shop_app.models import (
    Product,
    ProductImage,
    ProductCategory,
    CatagoryImage,
    Tag,
    SubCategory,
    SubCategoryImage,
    Review,
    Order,
    Sale,
    Specification,
    OrderProductCount,
)
from profile_app.models import Avatar, Profile


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
        )


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            "author",
            "email",
            "text",
            "rate",
            "date",
        )

    def get_author(self, obj):
        return obj.author.fullName

    def get_email(self, obj):
        return obj.author.email


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    tags = TagsSerializer(many=True)
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "fullDescription",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "specifications",
            "rating",
        ]

    def get_reviews(self, obj):
        result = Review.objects.filter(product=obj.pk)
        serializer = ReviewsSerializer(result, many=True)
        return serializer.data

    def get_rating(self, obj):
        result = Review.objects.filter(product=obj).aggregate(Avg("rate"))
        return result["rate__avg"] or 0

    def get_specifications(self, obj):
        result = Specification.objects.filter(product=obj.pk)
        return [{"name": product.name, "value": product.value} for product in result]

    def get_images(self, obj):
        images = [
            {"src": product.src.url, "alt": product.alt} for product in obj.images.all()
        ]
        return images

    def get_price(self, obj):
        if Sale.objects.filter(product=obj.pk):
            result = Sale.objects.get(product=obj.pk)
            return result.salePrice
        else:
            return obj.price


class SetProductsSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "available",
            "images",
            "tags",
            "reviews",
            "rating",
        ]

    def get_reviews(self, obj):
        result = Review.objects.filter(product=obj).aggregate(Count("product"))
        return result["product__count"]

    def get_rating(self, obj):
        result = Review.objects.filter(product=obj).aggregate(Avg("rate"))
        return result["rate__avg"] or 0

    def get_images(self, obj):
        images = [
            {"src": product.src.url, "alt": product.alt} for product in obj.images.all()
        ]
        return images

    def get_tags(self, obj):
        products = Tag.objects.filter(product=obj.pk)
        tags = [{"id": product.id, "name": product.name} for product in products]
        return tags

    def get_price(self, obj):
        if Sale.objects.filter(product=obj.pk):
            result = Sale.objects.get(product=obj.pk)
            return result.salePrice
        else:
            return obj.price


class SubcategorySerializer(serializers.ModelSerializer):
    # image = SubcategoryImageSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = (
            "id",
            "title",
            "image",
        )

    def get_image(self, obj):
        image = obj.image
        image = {"src": image.src.url, "alt": image.alt}
        return image


class ProductCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategory
        fields = "id", "title", "image", "subcategories"

    def get_image(self, obj):
        image = obj.image
        image = {"src": image.src.url, "alt": image.alt}
        return image


class SalesSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = "id", "price", "salePrice", "dateFrom", "dateTo", "title", "images"

    def get_price(self, obj):
        return obj.product.price

    def get_title(self, obj):
        return obj.product.title

    def get_images(self, obj):
        products = ProductImage.objects.select_related("product").filter(
            product_id=obj.product.id
        )
        images = [{"src": product.src.url, "alt": product.alt} for product in products]
        return images

    def get_id(self, obj):
        return obj.product.id


class AvatarSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = Avatar
        fields = (
            "src",
            "alt",
        )

    def get_src(self, obj):
        return obj.src.url


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "user_id",
            "fullName",
            "email",
            "phone",
            "avatar",
        )

    def get_avatar(self, obj):
        image = obj.avatar
        avatar = {"src": image.src.url, "alt": image.alt}
        return avatar


class UpdatePasswordSerializer(serializers.ModelSerializer):
    currentPassword = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = "currentPassword", "newPassword"


#
# class ProductOrderSerializer(serializers.ModelSerializer):
#     # id = serializers.SerializerMethodField()
#     count = serializers.SerializerMethodField()
#     images = serializers.SerializerMethodField()
#     tags = serializers.SerializerMethodField()
#     reviews = serializers.SerializerMethodField()
#     rating = serializers.SerializerMethodField()
#     price = serializers.SerializerMethodField()
#
#
#     class Meta:
#         model = Product
#         fields = [
#             'id', 'category', 'price', 'count', 'date', 'title', 'description',  'freeDelivery', 'available',
#             'images', 'tags', 'reviews', 'rating'
#         ]
#
#     def get_count(self, obj):
#         result= obj.order_products
#         pass
#
#     def get_reviews(self, obj):
#         result = Review.objects.filter(product=obj).aggregate(Count("product"))
#         return result['product__count']
#
#     def get_rating(self, obj):
#         result = Review.objects.filter(product=obj).aggregate(Avg('rate'))
#         return result['rate__avg'] or 0
#
#     def get_images(self, obj):
#         images = [
#             {"src": product.src.url, "alt": product.alt}
#             for product in obj.images.all()
#         ]
#         return images
#
#     def get_tags(self, obj):
#         products = Tag.objects.filter(product=obj.id)
#         tags = [{
#             'id': product.id, 'name': product.name
#         } for product in products]
#         return tags
#
#     def get_price(self, obj):
#         if Sale.objects.filter(product=obj.id):
#             result = Sale.objects.get(product=obj.id)
#             return result.salePrice
#         else:
#             return obj.price

# def get_category(self, obj):
#     return obj.product.category.id
#
# def get_date(self, obj):
#     return obj.product.date
#
# def get_description(self, obj):
#     return obj.product.description
#
# def get_freeDelivery(self, obj):
#     return obj.product.freeDelivery
#
# def get_title(self, obj):
#     return obj.product.title
#
# def get_available(self, obj):
#     return obj.product.available


class OrdersSerializer(serializers.ModelSerializer):
    # products = ProductOrderSerializer(many=True)
    products = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    fullName = serializers.SerializerMethodField()
    # deliveryType = serializers.SerializerMethodField()
    totalCost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        )

    def get_email(self, obj):
        return obj.profile.email

    def get_phone(self, obj):
        return obj.profile.phone

    def get_fullName(self, obj):
        return obj.profile.fullName

    def get_totalCost(self, obj):
        order = OrderProductCount.objects.filter(order_id=obj.id)
        total_cost = 0
        for item in order:
            product = Product.objects.get(id=item.product_id)
            total_cost += product.price * item.count_product
        return total_cost

    def get_products(self, obj):
        order = OrderProductCount.objects.filter(order_id=obj.id)
        cart_products = []
        total_cost = 0
        for item in order:
            product = Product.objects.get(id=item.product_id)
            cart_products.append(
                {
                    "id": product.id,
                    "category": product.category.id,
                    "price": product.price,
                    "count": item.count_product,
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

        return cart_products
