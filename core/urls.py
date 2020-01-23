from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    # item list
    path('', views.ItemListView.as_view(), name='product_list'),

    # item detail
    path('product/<slug>/', views.ItemDetailView.as_view(), name='product'),

    # add item to cart
    path('add-to-cart/<slug>/', views.add_to_cart, name='add_to_cart'),

    # remove item from cart
    path('remove-from-cart/<slug>/', views.remove_from_cart,
        name='remove_from_cart'),

    # order summary
    path('order-summary/', views.OrderSummaryView.as_view(),
        name='order_summary'),

    # remove single item from cart
    path('remove-single-item-from-cart/<slug>/',
        views.remove_single_item_from_cart,
        name='remove_single_item_from_cart'),

    # checkout
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),

    # payment
    path('payment/<payment_option>/', views.PaymentView.as_view(),
        name='payment'),

    # add coupon
    path('add_coupon/', views.AddCoupon.as_view(), name='add_coupon'),


    # request refund
    path('request-refund/', views.RequestRefundView.as_view(),
        name='request_refund'),
]
