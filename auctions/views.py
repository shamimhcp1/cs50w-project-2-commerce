from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required # on top of any view will ensure that only a user who is logged in can access that view.
from django.db.models import Max
from django.contrib import messages

from .models import User, Category, Listing, Bid


def index(request):
    listings = Listing.objects.filter(is_closed=False)
    return render(request, "auctions/index.html", {
        "listings" : listings
    })


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

@login_required(login_url='login')
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

# Listing Create
@login_required(login_url='login')
def create_listing(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        starting_bid = request.POST['starting_bid']
        image_url = request.POST['image_url']
        
        category = None
        if request.POST['category_id']:
            category = Category.objects.get(pk=request.POST['category_id'])
        
        seller = User.objects.get(pk=request.user.id)

        listing = Listing(title=title, description=description, starting_bid=starting_bid, image_url=image_url, category=category, seller=seller)
        listing.save()

        return HttpResponseRedirect(f"listings/{listing.id}")

    return render(request, "auctions/create_listing.html", {
        "categories" : categories
    })

# Edit Listing
@login_required(login_url='login')
def edit_listing(request, listing_id):
    categories = Category.objects.all()
    listing = Listing.objects.get(pk=listing_id)

    if request.method == "POST":

        category = None
        if request.POST['category_id']:
            category = Category.objects.get(pk=request.POST['category_id'])

        listing.title = request.POST['title']
        listing.description = request.POST['description']
        listing.starting_bid = request.POST['starting_bid']
        listing.image_url = request.POST['image_url']
        listing.category = category
        listing.save()

        return HttpResponseRedirect(reverse("single_listing", args=(listing.id,)))
    
    return render(request, "auctions/edit_listing.html", {
        "listing" : listing,
        "categories" : categories
    })

# Single Listing
def single_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    # Count total bid
    bids = Bid.objects.filter(listing_id=listing_id).order_by('-bid_amount')
    bids_count = len(bids)
    
    category = ""
    if listing.category_id:
        category = Category.objects.get(pk=listing.category_id)

    if request.method == "POST":
        try:
            # Try converting the input to a floating-point number
            bid_amount = float(request.POST.get('bid_amount'))
            starting_bid = listing.starting_bid
            
            # finding the max bid
            max_bid_amount = starting_bid
            if bids_count:
                max_bid = bids.aggregate(max_bid_amount=Max('bid_amount'))
                max_bid_amount = max_bid['max_bid_amount']
            
            # The bid must be at least as large as the starting bid, and must be greater than any other bids that have been placed (if any). 
            # If the bid doesn’t meet those criteria, the user should be presented with an error.
            if bid_amount > starting_bid and bid_amount > max_bid_amount :
                bid = Bid(bid_amount=bid_amount, bidder=request.user, listing=listing)
                bid.save()
                messages.success(request, f"Success! Bid amount: {bid_amount}")
                return HttpResponseRedirect(reverse("single_listing", args=(listing.id,)))
            else:
                raise ValueError
        except ValueError:
            # If the input is not a valid
            messages.warning(request, "Invalid input for bid amount")
            return HttpResponseRedirect(reverse("single_listing", args=(listing.id,)))
    
    messages_to_display = messages.get_messages(request)  # Get messages
    return render(request, "auctions/listing.html", {
        "listing" : listing,
        "category" : category,
        "bids_count" : bids_count,
        "messages" : messages_to_display,
        "bids" : bids
    })

# listing by seller/user
def listing_by_seller(request, seller_id):
    seller = User.objects.get(pk=seller_id)
    listings = Listing.objects.filter(seller_id=seller.id, is_closed=False)
    return render(request, "auctions/index.html", {
        "listings" : listings,
        "seller" : seller
    })

# listing by loged in user.
@login_required(login_url='login')
def my_listing(request):
    seller = User.objects.get(pk=request.user.id)
    listings = Listing.objects.filter(seller_id=seller.id)
    return render(request, "auctions/index.html", {
        "listings" : listings,
        "my_name" : seller
    })

def categories(request):
    all_categories = Category.objects.all()
    listings = Listing.objects.all()
    categories = set()
    for cat in all_categories:
        for list in listings:
            if cat.id == list.category_id:
                categories.add(cat)
    
    return render(request, "auctions/categories.html", {
        "categories" : categories,
        "listings" : listings
    })

def single_category(request, category_id):
    category = Category.objects.get(pk=category_id)
    listings = Listing.objects.filter(category_id=category_id)
    return render(request, "auctions/index.html", {
        "listings" : listings,
        "category" : category
    })

def no_category(request):
    listings = Listing.objects.filter(category_id=None)
    return render(request, "auctions/index.html", {
        "listings" : listings
    })
    
# Watchlist add or remove
@login_required(login_url='login')
def watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = User.objects.get(pk=request.user.id)
    
    if user in listing.watchers.all():
        listing.watchers.remove(user) # remove a listing from the watchlist if it already exists
        messages.warning(request, "Warning! Listing removed from watchlist.")
    else:
        listing.watchers.add(user) # add a listing to the watchlist not exists
        messages.success(request, f"Success! Listing added to watchlist.")
    
    return HttpResponseRedirect(reverse("single_listing", args=(listing.id,)))

# show list of watchlilst
@login_required(login_url='login')
def watchlist_show(request):
    listings = request.user.watchlist.all()
    return render(request, "auctions/index.html", {
        "listings" : listings,
        "watchlist_items" : "Watchlist Items"
    })

# close bid and set highest bidder
@login_required(login_url='login')
def close_bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)  # Retrieve the listing
    listing.close_auction()  # Manually close the auction

    messages.success(request, f"Success! Listing closed.")
    return HttpResponseRedirect(reverse("single_listing", args=(listing.id,)))