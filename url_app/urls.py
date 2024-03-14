from django.urls import path
from .views import *

urlpatterns = [
    path('', URLShortenerCreate.as_view(), name='url_shortener_create'),
    path('<str:shortened_url>/', redirect_to_original_url, name='redirect'),  
]