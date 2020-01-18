from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()


class Item(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title



class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.FloatField()

    def __str__(self):
        return self.item.title



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
