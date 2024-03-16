from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken


from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from .models import URLShortener
from .serializers import URLShortenerSerializer, ClickSerializer
from .forms import URLShortenerForm
from .serializers import CustomUserSerializer

import string
import random


class UserRegistration(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserLogin(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            if not email or not password:
                return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(request, email=email, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

def generate_short_url():
    ''' A Function to generate a random short URL '''
    characters = string.ascii_letters + string.digits
    short_url =  ''.join(random.choices(characters, k=5))
    print(short_url)
    return short_url



def redirect_to_original_url(request, shortened_url):
    '''
    function to redirect to the original URL when given the shortened URL.
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
    permission_classes = [IsAuthenticated]
    
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
                user = request.user

                new_url_shortener = URLShortener(original_url=original_url,
                                                 shortened_url=short_url,
                                                user=user
                                                )
                new_url_shortener.save()
                serializer = URLShortenerSerializer(new_url_shortener, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as err:
            print(err)
            return Response(form.errors)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class URLShortenerList(APIView):
    '''
    Get a list of all shortened URLs for the authenticated user
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        shortened_urls = URLShortener.objects.filter(user=user)
        serializer = URLShortenerSerializer(shortened_urls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class URLShortenerUpdate(APIView):
    '''
    Update the original URL of a shortened URL
    '''
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user = request.user
        try:
            url_shortener = URLShortener.objects.get(pk=pk, user=user)
        except URLShortener.DoesNotExist:
            return Response({'error': 'URL not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = URLShortenerSerializer(url_shortener, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class URLShortenerDelete(APIView):
    '''
    Delete a shortened URL
    '''
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        user = request.user
        try:
            url_shortener = URLShortener.objects.get(pk=pk, user=user)
        except URLShortener.DoesNotExist:
            return Response({'error': 'URL not found'}, status=status.HTTP_404_NOT_FOUND)

        url_shortener.delete()
        return Response({'message': 'URL deleted successfully'}, status=status.HTTP_204_NO_CONTENT)