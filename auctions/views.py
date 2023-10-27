from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

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
def create_listing(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        starting_bid = request.POST['starting_bid']
        image_url = request.POST['image_url']
        category = request.POST['category']
        
        return HttpResponse(f"{title}, {description}, {starting_bid}, {image_url}, {category}")

    return render(request, "auctions/create_listing.html")

# Single Listing
def single_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    seller = User.objects.get(pk=listing.seller_id)
    if listing.category_id:
        category = Category.objects.get(pk=listing.category_id)
    else:
        category = ""
    return render(request, "auctions/listing.html", {
        "listing" : listing,
        "category" : category,
        "seller" : seller
    })

def categories(request):
    all_categories = Category.objects.all()
    listings = Listing.objects.filter(is_closed=False)
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