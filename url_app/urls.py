from django.urls import path
from .views import *

urlpatterns = [
    path('', URLShortenerCreate.as_view(), name='url_shortener_create'),
    path('login/', UserLogin.as_view(), name='user_login'),
    path('register/', UserRegistration.as_view(), name='user_registration'),
    path('<str:shortened_url>/', redirect_to_original_url, name='redirect'),  
]