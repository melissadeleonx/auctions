from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required


from .models import User, Category, Listing, Comment, Bid

# Render the index page, passing the filtered active listings by category, all categories and the category_name of the selected category
def index(request):
    category_name = request.GET.get("category")    
    if category_name:
        listings = Listing.objects.filter(is_active=True, category__name=category_name)
    else:
        listings = Listing.objects.filter(is_active=True)
    
    all_categories = Category.objects.all()

    # Get message and message_type from query parameters
    message = request.GET.get("message", "")
    message_type = request.GET.get("message_type", "")

    context = {
    "listings": listings,
    "categories": all_categories,
    "category_name": category_name,
    "message": message,
    "message_type": message_type,
    }
    return render(request, "auctions/index.html", context)

# To filter the listing search form by category. Include the category name as query parameter to get a unique url when triggering the form submission
def category_filter(request, name):
    if request.method == "POST":
        try:
            category = get_object_or_404(Category, name=name)
            return HttpResponseRedirect(f"{reverse('index')}?category={category.name}")
        except Category.DoesNotExist:
            return HttpResponseRedirect(reverse("index"))

# Try the listing with id and also get its name parameters
# Get listing associated with the id
def listing(request, id):
    listing_page = get_object_or_404(Listing, pk=id)

    # Include context important to the listing
    all_comments = Comment.objects.filter(listing=listing_page)
    is_seller = request.user.username == listing_page.seller.username
    is_watchlist = request.user in listing_page.watchlist.all()

    # Get the name of the listing from the html request
    name = request.GET.get("name")

    # Check if the listing name query parameter exists
    if name:
        context = {
            "listing": listing_page,
            "is_watchlist": is_watchlist,
            "all_comments": all_comments,
            "is_seller": is_seller,
            "name": name,
        }
        return render(request, "auctions/listing.html", context) 
    else:
        # Use the standard listing template that only includes the id, include the listing, comments, watchlist status, seller information, and any messages
        context = {
            "listing": listing_page,
            "is_watchlist": is_watchlist,
            "all_comments": all_comments,
            "is_seller": is_seller,
            "message": request.GET.get("message", ""),  
            "message_type": request.GET.get("message_type", ""), 
        }
        return render(request, "auctions/listing.html", context)


# Allow signed-in users to remove an item from their watchlist, without leaving the page using HttpResponseRedirect.  
# login_required decorator ensures a user is authenticated before accessing certain pages and functionalities
@login_required
def remove_watchlist(request, id):
    listing_page = Listing.objects.get(pk=id)
    current_user = request.user
    listing_page.watchlist.remove(current_user)
    return HttpResponseRedirect(f"{reverse('listing', args=(id, ))}?message=The item is removed from your watchlist&message_type=danger")

# Allow signed-in users to add an item to their watchlist, redirect using the args parameter of the listing page
@login_required
def add_watchlist(request, id):
    listing_page = Listing.objects.get(pk=id)
    current_user = request.user
    listing_page.watchlist.add(current_user)
    return HttpResponseRedirect(f"{reverse('listing', args=(id, ))}?message=The item is added to your watchlist&message_type=success")

# Display the watchlist of the current user and retrieving it from the watchlist field of the Listing model related to the current user
@login_required
def watchlist(request):
    current_user = request.user
    user_watchlists = current_user.watchlist.all()
    return render(request, "auctions/watchlist.html", {"user_watchlists": user_watchlists})


# Add comment logic and store the comments for each listing using the Comments model.
@login_required
def add_comment(request, id):
    current_user = request.user
    listing_page = Listing.objects.get(pk=id)
    comment_text = request.POST['comment']

    comment = Comment(author=current_user, listing=listing_page, text=comment_text)
    comment.save() 
    
    return HttpResponseRedirect(f"{reverse('listing', args=(id, ))}?message=Your comment is added successfully.&message_type=success")

# Apply the create_listing logic to create html page
@login_required
def create_listing(request):
    if request.method == "GET":
        all_categories = Category.objects.all()
        return render(request, "auctions/create.html", {"categories": all_categories})
    elif request.method == "POST":
        # From the Listing model, create the form field
        title = request.POST.get("title")
        category_name = request.POST.get("category")
        description = request.POST.get("description")
        special_features = request.POST.get("special_features")
        image_url = request.POST.get("image_url")
        price = float(request.POST.get("price"))
        seller = request.user
        published_date= timezone.now() 

        # Connect the listing to a specific category by creating a category object
        category = Category.objects.get(name=category_name)

        # Create a bid object with the current_user as the bidder
        current_user = request.user

        bid = Bid(bid=float(price), bidder=current_user)
        bid.save()

        # With the submitted data, using create built in function, save the new listing
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
        return HttpResponseRedirect(f"{reverse('index')}?message=Thank you for adding your listing. Listing created successfully!&message_type=success")


@login_required
def add_bid(request, id):
    if request.method == "POST":
        # Get the new bid amount submitted by the user
        new_bid_added = (request.POST.get("new_bid"))
        new_bid = int(new_bid_added)
        listing_page = Listing.objects.get(pk=id)
        
        # Compare new bid with the current highest bid for the listing, if higher save it as the current bid.
        # Prompt a message for a success or failed bid
        if new_bid > listing_page.price.bid:
            current_bid = Bid(bidder=request.user, bid=new_bid)
            current_bid.save()
            listing_page.price = current_bid
            listing_page.save()         
            return HttpResponseRedirect(f"{reverse('listing', args=[id])}?message=You've placed a bid successfully!&message_type=success")
        else:
            return HttpResponseRedirect(f"{reverse('listing', args=[id])}?message=Failed bid. Please provide a higher amount than the current bid!&message_type=danger")


@login_required
def close_auction(request, id):
    # When closing the auction, make sure to set the is_active field to false
    listing_page = Listing.objects.get(pk=id)
    listing_page.is_active = False
    listing_page.save()

    # Check if the current user is the seller of the listing
    is_seller = request.user.username == listing_page.seller.username

    # Pass on other parameters necessary for the listing page
    is_watchlist = request.user in listing_page.watchlist.all()
    all_comments = Comment.objects.filter(listing=listing_page)

    context = {
    "listing": listing_page, 
    "is_watchlist": is_watchlist, 
    "all_comments": all_comments,
    "is_seller" : is_seller,
    "is_closed": True
    }
    return render(request, "auctions/listing.html", context)

# Added login url in the settings.py
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
