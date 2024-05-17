from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.db.models import Max

from .models import User, Category, Listing, Comment, Bid


def index(request):
    category_name = request.GET.get("category")
    if category_name:
        listings = Listing.objects.filter(is_active=True, category__name=category_name)
    else:
        listings = Listing.objects.filter(is_active=True)
    all_categories = Category.objects.all()
    return render(request, "auctions/index.html", {"listings": listings, "categories": all_categories, "category_name": category_name})

def category_filter(request, name):
    if request.method == "POST":
        try:
            category = get_object_or_404(Category, name=name)
            return HttpResponseRedirect(f"{reverse('index')}?category={category.name}")
        except Category.DoesNotExist:
            # Handle the case where the category does not exist
            return HttpResponseRedirect(reverse("index"))



# Add the title in the url to make the site more user-friendly
def listing(request, id):
    listing_page = Listing.objects.get(pk=id)
    is_watchlist = request.user in listing_page.watchlist.all()
    all_comments = Comment.objects.filter(listing=listing_page)
    is_seller = request.user.username == listing_page.seller.username
    return render(request, "auctions/listing.html", {"listing": listing_page, "is_watchlist": is_watchlist, "all_comments": all_comments, "is_seller": is_seller})

def remove_watchlist(request, id):
    listing_page = Listing.objects.get(pk=id)
    current_user = request.user
    listing_page.watchlist.remove(current_user)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def add_watchlist(request, id):
    listing_page = Listing.objects.get(pk=id)
    current_user = request.user
    listing_page.watchlist.add(current_user)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def watchlist(request):
    current_user = request.user
    user_watchlists = current_user.watchlist.all()
    return render(request, "auctions/watchlist.html", {"user_watchlists": user_watchlists})

def add_comment(request, id):
    current_user = request.user
    listing_page = Listing.objects.get(pk=id)
    comment_text = request.POST['comment']

    comment = Comment(author=current_user, listing=listing_page, text=comment_text)
    comment.save() 
    
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def create_listing(request):
    if request.method == "GET":
        # Pass on all Categories to the create page 
        all_categories = Category.objects.all()
        return render(request, "auctions/create.html", {"categories": all_categories})
    elif request.method == "POST":
        # Include the form fields
        title = request.POST.get("title")
        category_name = request.POST.get("category")
        description = request.POST.get("description")
        special_features = request.POST.get("special_features")
        image_url = request.POST.get("image_url")
        price = float(request.POST.get("price"))
        seller = request.user
        published_date= timezone.now() 

        category = Category.objects.get(name=category_name)

        current_user = request.user
        bid = Bid(bid=float(price), bidder=current_user)
        bid.save()

        # Create the new Listing instance
        new_listing = Listing.objects.create(
            title=title,
            category=category,
            description=description,
            special_features=special_features,
            image_url=image_url,
            price=bid,
            seller=seller,
            published_date=published_date
        )

        return HttpResponseRedirect(f"{reverse('index')}?success_message=Thank you for adding your listing. Listing created successfully!")
    
def add_bid(request, id):
    if request.method == "POST":
        new_bid_added = (request.POST.get("new_bid"))
        new_bid = int(new_bid_added)
        listing_page = Listing.objects.get(pk=id)
        is_watchlist = request.user in listing_page.watchlist.all()
        all_comments = Comment.objects.filter(listing=listing_page)
        
        if new_bid > listing_page.price.bid:
            current_bid = Bid(bidder=request.user, bid=new_bid)
            current_bid.save()
            listing_page.price = current_bid
            listing_page.save()
            return render(request, "auctions/listing.html", {
                "listing": listing_page, 
                "is_watchlist": is_watchlist, 
                "all_comments": all_comments,
                "success_bid": "You've placed a bid successfully! Thank you.",
                "is_updated": True})
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing_page, 
                "is_watchlist": is_watchlist, 
                "all_comments": all_comments,
                "failed_bid": "Failed! Sorry.",
                "is_updated": False})
        
def close_auction(request, id):
    listing_page = Listing.objects.get(pk=id)
    listing_page.is_active = False
    listing_page.save()
    is_seller = request.user.username == listing_page.seller.username
    is_watchlist = request.user in listing_page.watchlist.all()
    all_comments = Comment.objects.filter(listing=listing_page)
    
    return render(request, "auctions/listing.html", {
    "listing": listing_page, 
    "is_watchlist": is_watchlist, 
    "all_comments": all_comments,
    "is_seller" : is_seller,
    "is_closed": True})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
