from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    # item list
    path('', views.ItemListView.as_view(), name='product-list'),

    # item detail
    path('product/<slug>/', views.ItemDetailView.as_view(), name='product'),

    # add item to cart
    path('add-to-cart/<slug>/', views.add_to_cart, name='add_to_cart'),

    # remove item from cart
    path('remove-from-cart/<slug>/', views.remove_from_cart,
        name='remove_from_cart'),

    # order summary
    path('order-summary/', views.OrderSummary.as_view(), name='order-summary'),
]
