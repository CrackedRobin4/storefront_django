from typing import Any
from django.contrib import admin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.http.request import HttpRequest
from . import models

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'inventory_status', 'collection_title']
    list_editable = ['price']
    list_per_page = 10
    list_filter = ['collection', 'last_update']
    list_select_related = ['collection']

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 1000:
            return 'Low'
        else:
            return "Ok"
    
    def collection_title(self, product):
        return product.collection.title


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'member_ship', 'orders_count']
    list_editable = ['member_ship']
    list_per_page = 10
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istart_with', 'last_name__istart_with']

    @admin.display(ordering='orders_count')
    def orders_count(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + '?'
            + urlencode({
                'customer_id': str(customer.id)
            }))
        return format_html('<a href="{}">Orders count: {}</a>', url, customer.orders_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_first_name', 'customer_last_name', 'payment_status', 'placed_at']
    list_editable = ['payment_status']
    list_per_page = 10
    list_select_related = ['customer']
    ordering = ['placed_at']

    def customer_first_name(self, order):
        return order.customer.first_name
    
    def customer_last_name(self, order):
        return order.customer.last_name

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (
            reverse('admin:store_product_changelist') 
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            }))
        return format_html('<a href="{}">{}</a>', url, collection.products_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )