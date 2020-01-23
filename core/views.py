from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from .models import (
    Order,
    OrderItem,
    Item,
    Address,
    Payment,
    Coupon,
    Refund,
)
from .forms import (
    CheckoutForm,
    CouponForm,
    RefundForm,
)

import stripe
stripe.api_key = settings.API_SECRET_KEY

import string
import random


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))



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
            return redirect('core:order_summary')
        else:
            messages.info(request, "This item was added to your cart.")
            order_item.quantity = 1
            order_item.save()
            order.items.add(order_item)
            return redirect('core:order_summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,
            ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect('core:order_summary')



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



def remove_single_item_from_cart(request, slug):
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
            if order_item.quantity == 1:
                order.items.remove(order_item)
                messages.info(request, "This item was removed from your cart.")
                return redirect('core:order_summary')
            elif order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                return redirect('core:order_summary')
            else:
                messages.info(request, "Operation failed.")
                return redirect('core:order_summary')
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



class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=request.user, ordered=False)
        coupon_form = CouponForm()

        context = {
            'form': form,
            'order': order,
            'coupon_form': coupon_form,
            'DISPLAY_COUPON_FORM': True,
        }
        return render(request, 'checkout.html', context)

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST or None)
        order = Order.objects.get(user=request.user, ordered=False)

        if form.is_valid():
            cd = form.cleaned_data
            street_address = cd.get('street_address')
            apartment_address = cd.get('apartment_address')
            country = cd.get('country')
            zip = cd.get('zip')
            # same_shipping_address = cd.get('same_shipping_address')
            # save_info = cd.get('save_info')
            payment_option = cd.get('payment_option')

            billing_address = Address.objects.create(user=request.user,
                street_address=street_address,
                apartment_address=apartment_address,
                country=country,
                zip=zip,
                address_type='B'
            )

            order.billing_address = billing_address
            order.save()

            if payment_option == 'S':
                return redirect('core:payment', payment_option='stripe')
            elif payment_option == 'P':
                return redirect('core:payment', payment_option='paypal')
            else:
                messages.warning(request, 'Invalid payment option selected')
                return redirect('core:checkout')
        else:
            return redirect("core:checkout")



class PaymentView(View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=request.user, ordered=False)

        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
            }

            return render(request, 'payment.html', context)
        else:
            messages.warning(request, "You have not added a billing address")
            return redirect("core:checkout")


    def post(self, request, *args, **kwargs):
        token = request.POST.get('stripeToken')
        order = Order.objects.get(user=request.user, ordered=False)
        amount = int(order.get_total() * 100) # cents

        try:
            # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                amount=amount, # cents
                currency='usd',
                source=token,
                # idempotency_key='sgOsfVXOkax5Ma8m'
            )

            # create the payment
            payment = Payment.objects.create(
                stripe_charge_id=charge['id'],
                user=request.user,
                amount=order.get_total()
            )

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            messages.success(request, 'Your order was successful!')
            return redirect('core:product_list')

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            messages.warning(request, e.error.message)
            return redirect('core:product_list')

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(request, "Rate limit error.")
            return redirect('core:product_list')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(request, "Invalid parameters.")
            return redirect('core:product_list')

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(request, "Not authenticated.")
            return redirect('core:product_list')

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(request, "Network error.")
            return redirect('core:product_list')

        except stripe.error.StripeError as e:
            messages.warning(request, "Something went wrong. You were not charged. Plase try again.")
            return redirect('core:product_list')

        except Exception as e:
            messages.warning(request, "A serious error occurred. We have been notified.")
            return redirect('core:product_list')



def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist.")
        return redirect('core:checkout')



class AddCoupon(View):
    def post(self, request, *args, **kwargs):
        form = CouponForm(request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=request.user, ordered=False)
                coupon = get_coupon(request, code)
                order.coupon = coupon
                order.save()
                messages.success(request, "Successfully added coupon.")
                return redirect('core:checkout')
            except ObjectDoesNotExist:
                messages.info(request, "You do not have an active order")
                return redirect('core:checkout')
        messages.warning(request, "Could not process the request!")
        return redirect("core:checkout")



class RequestRefundView(View):
    def get(self, request, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form,
        }
        return render(request, 'request_refund.html', context)


    def post(self, request, *args, **kwargs):
        form = RefundForm(request.POST or None)
        if form.is_valid():
            cd = form.cleaned_data
            ref_code = cd.get('ref_code')
            message = cd.get('message')
            email = cd.get('email')
            
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.success(request, 'Your request was received.')
                return redirect('core:request_refund')

            except ObjectDoesNotExist:
                messages.warning(request, 'This order does not exist.')
                return redirect('core:request_refund')
