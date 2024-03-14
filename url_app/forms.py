from django import forms

class URLShortenerForm(forms.Form):
    original_url = forms.URLField(label='Original URL')