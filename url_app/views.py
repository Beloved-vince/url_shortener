from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import URLShortenerSerializer, ClickSerializer
from .models import URLShortener
import string
import random
from .forms import URLShortenerForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect




def generate_short_url():
    ''' A Function to generate a random short URL '''
    characters = string.ascii_letters + string.digits
    short_url =  ''.join(random.choices(characters, k=5))
    print(short_url)
    return short_url



def redirect_to_original_url(request, shortened_url):
    '''
    View to redirect to the original URL when given the shortened URL.
    Increments the clicks count for the shortened URL.
    '''
    url_shortener = get_object_or_404(URLShortener, shortened_url=shortened_url)
    url_shortener.clicks += 1
    url_shortener.save()
    return HttpResponseRedirect(url_shortener.original_url)
class URLShortenerCreate(APIView):
    '''
        Check if the URL is already shortened
        Generate a new short URL
        Create and save the new URLShortener object
        Serialize the new object and return it
    '''
    def post(self, request):
        form = URLShortenerForm(request.data)
        try:
            if form.is_valid():
                original_url = form.cleaned_data['original_url']
                existing_shortened_url = URLShortener.objects.filter(original_url=original_url).first()
                
                if existing_shortened_url:
                    serializer = URLShortenerSerializer(existing_shortened_url, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)

                short_url = generate_short_url()
                new_url_shortener = URLShortener(original_url=original_url, shortened_url=short_url)
                new_url_shortener.save()
                serializer = URLShortenerSerializer(new_url_shortener, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as err:
            print(err)
            return Response(form.errors)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
    