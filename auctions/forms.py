from django import forms
from .models import Listing, Bid, Comment

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'description', 'special_features', 'image_url', 'starting_price']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']