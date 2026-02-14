import platform
from rest_framework import serializers
from accounts.serializers import SellerProfileSerializer
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'unit']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'
        read_only_fields = ['product']


class ProductSerializer(serializers.ModelSerializer):
    # read only 
    images = ProductImageSerializer(many=True, read_only=True) 
    seller = SellerProfileSerializer(read_only=True)
    category_detail = CategoryReadSerializer(source='category', read_only=True)

    # write only 
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(is_active=True), write_only=True)
    uploaded_images  = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = ['id', 'seller', 'category', 'category_detail', 'name', 'description', 'price_per_unit', 'unit', 'available_quantity', 'min_order_quantity', 'is_organic', 'harvest_date', 'is_active', 'created_at', 'updated_at', 'images', 'uploaded_images']
        read_only_fields = ['seller', 'created_at', 'updated_at', 'images', 'category_detail']


    def create(self, validated_data):
        images_data = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(**validated_data)
        for image_data in images_data:
            ProductImage.objects.create(product=product, image=image_data)
        return product
    
    def update(self, instance, validated_data):
        images_data = validated_data.pop('uploaded_images', [])
        instance = super().update(instance, validated_data)

        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, image=image_data)

        return instance
    