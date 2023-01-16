from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


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
   isListingWatchlisted = request.user in listingInfo.watchlist.all()
   allComments = Comment.objects.filter(listing=listingInfo)
   isOwner = request.user.username == listingInfo.owner.username
   return render(request, "auctions/listing.html", {
      "listing": listingInfo,
      "isListingWatchlisted": isListingWatchlisted,
      "allComments": allComments,
      "isOwner": isOwner
   })

def closeAuction(request, id):
   listingInfo = Listing.objects.get(pk=id)
   listingInfo.isActive = False
   listingInfo.save()
   isListingWatchlisted = request.user in listingInfo.watchlist.all()
   allComments = Comment.objects.filter(listing=listingInfo)
   isOwner = request.user.username == listingInfo.owner.username
   return render(request, "auctions/listing.html", {
       "listing": listingInfo,
       "isListingWatchlisted": isListingWatchlisted,
       "allComments": allComments,
       "isOwner": isOwner,
       "update": True,
       "message": "The auction has closed."
   })

def addBid (request, id):
   newBid = request.POST['newBid']
   listingInfo = Listing.objects.get(pk=id)
   isListingWatchlisted = request.user in listingInfo.watchlist.all()
   allComments = Comment.objects.filter(listing=listingInfo)
   isOwner = request.user.username == listingInfo.owner.username
   if int(newBid) > listingInfo.price.bid:
      updateBid = Bid(user=request.user, bid=int(newBid))
      updateBid.save()
      listingInfo.price = updateBid
      listingInfo.save()
      return render(request, "auctions/listing.html", {
         "listing": listingInfo,
         "message": "Bid was successful.",
         "update": True,
         "isListingWatchlisted": isListingWatchlisted,
         "allComments": allComments,
         "isOwner": isOwner
      })
   else:
      return render(request, "auctions/listing.html", {
          "listing": listingInfo,
          "message": "Bid attempt failed.",
          "update": False,
          "isListingWatchlisted": isListingWatchlisted,
          "allComments": allComments,
          "isOwner": isOwner
      })
 

def addComment(request, id):
   currentUser = request.user
   listingInfo = Listing.objects.get(pk=id)
   message = request.POST['newComment']

   newComment = Comment(
      author=currentUser,
      listing=listingInfo,
      message=message
   )

   newComment.save()

   return HttpResponseRedirect(reverse("listing", args=(id, )))

def displayWatchlist(request):
   currentUser = request.user
   listings = currentUser.listingWatchlist.all()
   return render(request, "auctions/watchlist.html", {
      "listings": listings
   })

def addToWatchlist(request, id):
   listingInfo = Listing.objects.get(pk=id)
   currentUser = request.user
   listingInfo.watchlist.add(currentUser)
   return HttpResponseRedirect(reverse("listing", args=(id, )))

def removeFromWatchlist(request, id):
   listingInfo = Listing.objects.get(pk=id)
   currentUser = request.user
   listingInfo.watchlist.remove(currentUser)
   return HttpResponseRedirect(reverse("listing", args=(id, )))

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
      # create bid object
      bid = Bid(bid=int(price), user=currentUser)
      bid.save()
      # create new listing object
      newListing = Listing(
         title=title,
         description=description,
         imageURL=imageURL,
         price=bid,
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
