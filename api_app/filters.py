import django_filters
from django_filters.rest_framework import FilterSet
from django_filters import FilterSet

from shop_app.models import Product


class CatalogFilter(FilterSet):
    title = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Product
        fields = [
            "price",
        ]
