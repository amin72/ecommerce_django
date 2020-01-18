from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Order, OrderItem, Item


class ItemListView(ListView):
    model = Item
    template_name = 'home.html'
