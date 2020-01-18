from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    # item list
    path('', views.ItemListView.as_view(), name='product-list'),

    # item detail
    path('product/<slug>/', views.ItemDetailView.as_view(), name='product'),
]
