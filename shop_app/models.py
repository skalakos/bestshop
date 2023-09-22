from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from profile_app.models import Profile


def product_preview_dir_path(instanse: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instanse.pk,
        filename=filename,
    )


class Product(models.Model):
    """Модель товара"""

    AVAILABLE_CHOICES = [
        ("true", _("true")),
        ("false ", _("false")),
    ]

    class Meta:
        ordering = ["title", "price"]
        verbose_name_plural = _("products")
        verbose_name = _("product")

    title = models.CharField(max_length=100, verbose_name=_("name"))
    description = models.CharField(
        max_length=120, blank=True, verbose_name=_("description")
    )
    fullDescription = models.TextField(
        null=True, blank=True, verbose_name=_("full description")
    )
    price = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, verbose_name=_("price")
    )
    archived = models.BooleanField(default=False, verbose_name=_("archived"))
    preview = models.ImageField(
        null=True,
        blank=True,
        upload_to=product_preview_dir_path,
        verbose_name=_("preview"),
    )
    category = models.ForeignKey(
        "ProductCategory",
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("category"),
    )
    count = models.IntegerField(default=0, verbose_name=_("quantity"))
    tags = models.ManyToManyField("Tag", verbose_name=_("tag"))
    freeDelivery = models.BooleanField(default=False, verbose_name=_("delivery"))
    date = models.DateTimeField(auto_now_add=True, null=True, verbose_name=_("date"))
    # available = models.BooleanField(default=False, verbose_name=_('available'))
    available = models.CharField(
        choices=AVAILABLE_CHOICES, max_length=30, null=True, default="true"
    )
    # sale = models.ForeignKey('Sale', null=True, on_delete=models.PROTECT, related_name='product')

    def __str__(self) -> str:
        name = _("product")
        return f"{name} (pk={self.pk}; {self.title!r})"


def prod_image_dir_path(instanse: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instanse.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    """Модель для изображения товара"""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    src = models.ImageField(upload_to=prod_image_dir_path, verbose_name=_("image"))
    alt = models.CharField(
        max_length=250, null=False, blank=True, verbose_name=_("description")
    )

    class Meta:
        verbose_name_plural = _("images")
        verbose_name = _("image")


class ProductCategory(models.Model):
    """Модель для категории товара"""

    class Meta:
        ordering = ["title"]
        verbose_name_plural = _("categories")
        verbose_name = _("category")

    title = models.CharField(max_length=100, verbose_name=_("title"))
    description = models.TextField(
        null=False, blank=True, verbose_name=_("description")
    )

    def __str__(self) -> str:
        return f" {self.title}"


def category_image_dir_path(instanse: "ProductCategory", filename: str) -> str:
    return "categories/category_{pk}/images/{filename}".format(
        pk=instanse.category.pk,
        filename=filename,
    )


class CatagoryImage(models.Model):
    """Модель иконки для категории товара"""

    category = models.OneToOneField(
        ProductCategory, on_delete=models.CASCADE, related_name="image"
    )
    src = models.ImageField(
        upload_to=category_image_dir_path,
    )
    alt = models.CharField(
        max_length=250,
        null=False,
        blank=True,
    )

    class Meta:
        verbose_name_plural = _("images")
        verbose_name = _("image")


class SubCategory(models.Model):
    class Meta:
        verbose_name_plural = _("subcategories")
        verbose_name = _("subcategory")

    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name="subcategories"
    )
    title = models.CharField(max_length=250, null=True)

    def __str__(self):
        return self.title


def sub_category_image_dir_path(instanse: "SubCategory", filename: str) -> str:
    return "subcategories/subcategory_{pk}/images/{filename}".format(
        pk=instanse.pk,
        filename=filename,
    )


class SubCategoryImage(models.Model):
    subcategory = models.OneToOneField(
        SubCategory, on_delete=models.CASCADE, related_name=_("image")
    )
    src = models.ImageField(
        upload_to=sub_category_image_dir_path, verbose_name=_("image")
    )
    alt = models.CharField(
        max_length=250, null=False, blank=True, verbose_name=_("description")
    )

    class Meta:
        verbose_name_plural = _("images")
        verbose_name = _("image")


class Order(models.Model):
    STATUS_CHOICES = [
        ("unfinished", _("Unfinished")),
        ("confirmed", _("Confirmed")),
        ("paid", _("Paid")),
        ("collected", _("Collected")),
        ("delivered", _("Delivered")),
    ]

    PAYMENT_CHOICES = [
        ("online", _("ONLINE")),
        ("cash", _("CASH")),
    ]

    DELIVERY_CHOICES = [
        ("free", _("FREE")),
        ("paid ", _("PAID")),
    ]

    city = models.CharField(null=False, max_length=50, verbose_name=_("city"))
    address = models.TextField(null=False, blank=True, verbose_name=_("address"))
    createdAt = models.DateTimeField(
        auto_now_add=True, null=False, blank=True, verbose_name=_("created_time")
    )
    paymentType = models.CharField(
        choices=PAYMENT_CHOICES,
        max_length=50,
        default=_("cash"),
        verbose_name=_("payment"),
    )
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, verbose_name=_("user")
    )
    products = models.ManyToManyField(
        Product, related_name="orders", verbose_name=_("product")
    )
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=30,
        default="unfinished",
        verbose_name=_("status"),
    )
    deliveryType = models.CharField(
        choices=DELIVERY_CHOICES, max_length=30, null=True, default=None
    )

    def __str__(self):
        return f"Order{self.pk}, {self.profile.fullName}"


class OrderProductCount(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_products"
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orders")
    count_product = models.PositiveIntegerField(default=1)


class Review(models.Model):
    """Модель для отзыва товара"""

    author = models.ForeignKey(
        Profile,
        null=True,
        on_delete=models.CASCADE,
        related_name="author",
        verbose_name=_("user_id"),
    )
    # author = models.CharField(max_length=150,  null=True, verbose_name=_('author'))
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="review",
        verbose_name=_("product_id"),
    )
    label = models.CharField(max_length=100, verbose_name=_("label"))
    text = models.TextField(null=False, blank=True, verbose_name=_("description"))
    date = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name=_("date")
    )
    rate = models.DecimalField(
        default=0, max_digits=3, decimal_places=2, verbose_name=_("rating")
    )


class Tag(models.Model):
    """Модель тэга"""

    name = models.CharField(max_length=100, verbose_name=_("tag"))

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")

    def __str__(self):
        return self.name


class Sale(models.Model):
    """Модель для товара учавствующего в распродаже"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sale")
    salePrice = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, verbose_name=_("sale")
    )
    dateFrom = models.DateField(
        auto_now=False, null=True, blank=True, verbose_name=_("date_from")
    )
    dateTo = models.DateField(
        auto_now=False, null=True, blank=True, verbose_name=_("date_to")
    )

    def __str__(self):
        return f"{self.salePrice}"


class Specification(models.Model):
    """Модель для спецификации товара"""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="specification"
    )
    name = models.CharField(max_length=150, null=True, blank=True)
    value = models.CharField(max_length=250)
