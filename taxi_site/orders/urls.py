from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/drivers/", views.api_drivers, name="api_drivers"),
    path("api/order/", views.api_order, name="api_order"),
]
