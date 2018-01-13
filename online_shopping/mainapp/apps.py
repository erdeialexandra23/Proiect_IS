# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class MainappConfig(AppConfig):
    name = 'mainapp'

class OrdersConfig(AppConfig):
    name = 'orders'

class CartConfig(AppConfig):
    name = 'cart'