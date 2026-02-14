import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price_per_unit", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price_per_unit", lookup_expr="lte")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    category = django_filters.CharFilter(field_name="category__name", lookup_expr="iexact")
    is_organic = django_filters.BooleanFilter(field_name="is_organic")

    class Meta:
        model = Product
        fields = ["min_price", "max_price", "name", "category", "is_organic"]