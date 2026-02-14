from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from decimal import Decimal
from product.permissions import IsAdmin
from .serializers import PlatformCommissionSerializer, PlatformRevenueSerializer
from .models import PlatformCommission, PlatformRevenue
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class PlatformCommissionViewSet(viewsets.ModelViewSet):
    queryset = PlatformCommission.objects.all()
    serializer_class = PlatformCommissionSerializer
    http_method_names = ['get', 'put', 'patch']
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return PlatformCommission.objects.filter(id=1)


class PlatformRevenueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlatformRevenue.objects.all()
    serializer_class = PlatformRevenueSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['revenue_type', 'seller', 'buyer']
    search_fields = ['transaction_id', 'description']
    ordering_fields = ['amount', 'created_at']

    def get_queryset(self):
        return PlatformRevenue.objects.select_related(
            'order', 'seller', 'buyer'
        ).all()
    
    # total revenue 
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Start date in YYYY-MM-DD format'
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description='End date in YYYY-MM-DD format'
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def total(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        total = PlatformRevenue.get_total_revenue(start_date, end_date)

        return Response({
            "total_revenue": total
        })
    
    # monthly revenue
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='year',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Year (e.g., 2026)'
            ),
            OpenApiParameter(
                name='month',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Month number (1-12)'
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def monthly(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        if year:
            year = int(year)
        if month:
            month = int(month)

        total = PlatformRevenue.get_monthly_revenue(year, month)

        return Response({
            "year": year,
            "month": month,
            "monthly_revenue": total
        })


