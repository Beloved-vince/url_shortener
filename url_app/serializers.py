from rest_framework import serializers
from .models import URLShortener, Click
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'is_active', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    

class URLShortenerSerializer(serializers.ModelSerializer):
    shortened_url = serializers.SerializerMethodField()
    
    class Meta:
        model = URLShortener
        fields = ['user','id', 'original_url', 'shortened_url', 'clicks', 'created_at']
        
    def get_shortened_url(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.shortened_url)
        print(obj.shortened_url)
        return obj.shortened_url

class ClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Click
        fields = ['id', 'url_shortener', 'clicked_at']