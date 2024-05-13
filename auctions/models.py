from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone



class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):  
        return self.name

class Bid(models.Model):
    bid= models.IntegerField(default=0)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="bidder")

    def __str__(self):  
        return str(self.bid)

class Listing(models.Model):
    title = models.CharField(max_length=64)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    description = models.TextField()
    special_features = models.CharField(max_length=500, null=True)
    image_url = models.CharField(max_length=1000, null=True)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bid_amount") 
    is_active = models.BooleanField(default=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="seller")
    published_date = models.DateTimeField(default=timezone.now, null=True )
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="watchlist")


    def __str__(self):  
        return self.title

    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="author")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing")
    text = models.TextField()
    published_date = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):  
        return f"comment from {self.author} for {self.listing}"
    
