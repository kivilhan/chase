from django.contrib import admin
from django.urls import path
from .views import (TraderListView,
                    TraderPosListView,
                    TraderOrderListView)

urlpatterns = [
    path('', TraderListView.as_view(), name='chase-home'),
    path('positions/<str:title>', TraderPosListView.as_view(), name='trader-pos'),
    path('orders/<str:title>', TraderOrderListView.as_view(), name='trader-order'),
]
