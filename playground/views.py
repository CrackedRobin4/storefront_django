from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from store.models import Product, OrderItem

def say_hello(request):
    query_set = Product.objects.filter(
        id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')

    return render(request, 'hello.html', { 'name': 'Miras', 'products': list(query_set)})