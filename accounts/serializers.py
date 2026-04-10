from rest_framework import serializers
from order.models import Order
from .models import User, SellerProfile, BuyerProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    # common fields 
    nid_number = serializers.CharField(max_length=20, required=True)
    division = serializers.CharField(max_length=50, required=True)
    district = serializers.CharField(max_length=50, required=True)
    upazila = serializers.CharField(max_length=50, required=True)
    village = serializers.CharField(max_length=100, required=True)
    address_details = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'user_type', 
                  'password', 'confirm_password', 'nid_number', 'division', 'district', 'upazila', 'village', 'address_details']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        
        if User.objects.filter(phone=data['phone']).exists():
            raise serializers.ValidationError("Phone number already in use.")
        
        if data['user_type'] == 'seller':
            if not data.get('nid_number'):
                raise serializers.ValidationError("NID number is required for sellers.")
            if SellerProfile.objects.filter(nid_number=data['nid_number']).exists():
                raise serializers.ValidationError("NID number already in use for a seller.")
        elif data['user_type'] == 'buyer':
            if not data.get('nid_number'):
                raise serializers.ValidationError("NID number is required for buyers.")
            if BuyerProfile.objects.filter(nid_number=data['nid_number']).exists():
                raise serializers.ValidationError("NID number already in use for a buyer.")

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        user.is_verified = False
        user.save()
        if user.user_type == 'seller':
            SellerProfile.objects.create(
                user=user,
                nid_number=validated_data['nid_number'],
                division=validated_data['division'],
                district=validated_data['district'],
                upazila=validated_data['upazila'],
                village=validated_data['village'],
                address_details=validated_data.get('address_details', '')
            )
        elif user.user_type == 'buyer':
            BuyerProfile.objects.create(
                user=user,
                nid_number=validated_data['nid_number'],
                division=validated_data['division'],
                district=validated_data['district'],
                upazila=validated_data['upazila'],
                village=validated_data['village'],
                address_details=validated_data.get('address_details', '')
            )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_type'] = user.user_type 
        return token


class ForgetOrChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class SetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'user_type', 'profile_image', 'is_verified', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at', 'is_deleted']


class SellerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = SellerProfile
        fields = ['id', 'user', 'nid_number', 'division', 'district', 'upazila', 'village', 'address_details']


class BuyerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = BuyerProfile
        fields = ['id', 'user', 'nid_number', 'division', 'district', 'upazila', 'village', 'address_details']



class SellerDashboardSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    products = products = serializers.SerializerMethodField()
    class Meta:
        model = SellerProfile
        fields = [
            'user',
            'products',
            'nid_number',
            'division',
            'district',
            'upazila',
            'village',
            'address_details',
        ]

    def get_products(self, obj):
        from product.serializers import ProductSerializer 
        products = obj.products.all()
        return ProductSerializer(products, many=True).data


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'



class BuyerDashboardSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    orders = serializers.SerializerMethodField()

    class Meta:
        model = BuyerProfile
        fields = [
            'user',
            'orders',
            'nid_number',
            'division',
            'district',
            'upazila',
            'village',
            'address_details',
        ]

    def get_orders(self, obj):
        orders = obj.orders.all()
        return OrderSerializer(orders, many=True).data