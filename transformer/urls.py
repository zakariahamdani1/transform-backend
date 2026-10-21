from django.urls import path
from .views import test_api, get_shopify_columns

urlpatterns = [
    path('test/', test_api),
    path('shopify-columns/', get_shopify_columns),
]