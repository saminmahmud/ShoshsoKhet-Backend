import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category__id")
    seller = django_filters.NumberFilter(field_name="seller__id")
    class Meta:
        model = Product
        fields = ["category", "seller"]