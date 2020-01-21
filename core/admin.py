from django.contrib import admin
from .models import Order, OrderItem, Item, Payment, BillingAddress


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(BillingAddress)
