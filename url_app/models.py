from django.db import models

class URLShortener(models.Model):
    original_url = models.URLField(max_length=2000)
    shortened_url = models.CharField(max_length=50, unique=True)
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.short_url

class Click(models.Model):
    url_shortener = models.ForeignKey(URLShortener, on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url_shortener.short_url