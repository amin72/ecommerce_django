from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    path('', views.ItemListView.as_view(), name='item-list'),
]
