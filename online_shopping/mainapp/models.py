# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.core.urlresolvers import reverse
import random,os
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.core.mail import send_mail
from decimal import Decimal

from django.conf import settings

# Create your models here.

def get_filename_ext(filepath):
     base_name = os.path.basename(filepath)
     name, ext = os.path.splitext(base_name)
     return name, ext

def upload_image_path(self,instance,filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "products/{new_filename}/{final_filename}".format(
            new_filename = new_filename,
            final_filename = final_filename
            )
GENDER_CHOICES = ( ('M','Male'), ('F', 'Female'))
SIZE_CHOICES = (('XS','XS'),('S','S'),('M','M'),('L','L'))
CLOTHES_CHOICES=(('Shirt','Shirts'),('Dress','Dresses'),('Sweater','Sweaters'),('Coat','Coat&Jackets'),('Jeans','Jeans'),('Skirt','Skirts'),('Shoes','Shoes'))
class Product(models.Model):
    category = models.CharField(choices=CLOTHES_CHOICES,max_length=20)
    name = models.CharField(max_length=50)
    productID=models.AutoField(primary_key=True)
    sex=models.CharField(max_length=10,choices=GENDER_CHOICES)
    amount=models.IntegerField()
    price=models.FloatField()
    size=models.CharField(max_length=2,choices=SIZE_CHOICES)
    description=models.TextField()
    image=None

    def __str__(self):  #how to print it
        return self.name #{self.category, self.name, self.price, self.amount, self.size, self.description }

class Image(models.Model):
    product=models.ForeignKey(Product)
    image=models.ImageField(upload_to='product_photo', blank=True)

    def __str__(self):
        return str(self.product)+' '+str(self.image)

class Customer(models.Model):
    user = models.OneToOneField(User)
    username = models.CharField(max_length=30)
    first_name=models.CharField(max_length=30)
    last_name=models.CharField(max_length=30)
    email=models.CharField(max_length=30)
    #phone=models.CharField(max_length=12)
    #address=models.CharField(max_length=100)
    password=models.CharField(max_length=20)

    def __str__(self):  #how to print it
       return self.first_name

    def get_absolute_url(self):
        return reverse('mainapp:profile',kwargs={'id':self.pk})



#----orders-----

class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    #postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              related_name='items')
    product = models.ForeignKey(Product,
                                related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity

    #---------cart--------

class Cart(object):
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # update the session cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # mark the session as "modified" to make sure it is saved
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True



def cart(request):
            return {'cart': Cart(request)}