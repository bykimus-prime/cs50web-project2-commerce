from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing


def index(request):
   activeListings = Listing.objects.filter(isActive=True)
   allCategories = Category.objects.all()
   return render(request, "auctions/index.html", {
      "listings": activeListings,
      "categories": allCategories
    })

def displayCategory(request):
   if request.method == "POST":
      categoryFormIntake = request.POST['category']
      category = Category.objects.get(categoryName=categoryFormIntake)
      activeListings = Listing.objects.filter(isActive=True, category=category)
      allCategories = Category.objects.all()
      return render(request, "auctions/index.html", {
         "listings": activeListings,
         "categories": allCategories
      })

def listing(request, id):
   listingInfo = Listing.objects.get(pk=id)
   isListingWatchlisted = False
   return render(request, "auctions/listing.html", {
      "listing": listingInfo,
      "isListingWatchlisted": isListingWatchlisted
   })

def removeFromWatchlist(request, id):
   return

def addToWatchlist(request, id):
   return

def createListing(request):
   if request.method == "GET":
      allCategories = Category.objects.all()
      return render(request, "auctions/create-listing.html", {
         # name on left in orange is html, right is python
         "categories": allCategories
      })
   else:
      # get data from create-listing.html form
      title = request.POST["title"]
      description = request.POST["description"]
      imageURL = request.POST["imageURL"]
      price = request.POST["price"]
      category = request.POST["category"]

      # user info
      currentUser = request.user

      # get content from needed category
      categoryData = Category.objects.get(categoryName=category)

      # create new listing object
      newListing = Listing(
         title=title,
         description=description,
         imageURL=imageURL,
         price=float(price),
         category=categoryData,
         owner=currentUser
      )

      # insert object into database
      newListing.save()

      # redirect to index page
      return HttpResponseRedirect(reverse(index))

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
