# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from mainapp.models import Product,Image,Customer, Order, OrderItem

# Register your models here.
#admin.site.register(Product)


class InlineImage(admin.TabularInline):
    model = Image


class ProductAdmin(admin.ModelAdmin):
    inlines = [InlineImage]

admin.site.register(Product, ProductAdmin)
admin.site.register(Customer)

#-------order------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email',
                    'address', 'city', 'completed',
                    'created', 'updated']
    list_filter = ['completed', 'created', 'updated']
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)