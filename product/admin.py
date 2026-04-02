from django.contrib import admin
from .models import Product, Category, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)
    ordering = ('name',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price_per_unit', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'category')
    ordering = ('-created_at',)
    inlines = [ProductImageInline]

    