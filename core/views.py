from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, OrderItem, Item


class ItemListView(ListView):
    model = Item
    template_name = 'home.html'
    paginate_by = 20



class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'



def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the order item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect('core:product', slug=slug)
        else:
            messages.info(request, "This item was added to your cart.")
            order.items.add(order_item)
            return redirect('core:product', slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,
            ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect('core:product', slug=slug)



def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect('core:product', slug=slug)
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, "You do not have an active order.")
        return redirect('core:product', slug=slug)



class OrderSummaryView(LoginRequiredMixin, View):
    template_name = 'order_summary.html'

    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            return render(request, 'order_summary.html', {'object': order})
        except ObjectDoesNotExist:
            messages.error(request, "You do not have an active order")
            return redirect('/')
