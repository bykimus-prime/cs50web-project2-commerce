from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createListing", views.createListing, name="createListing"),
    path("displayCategory", views.displayCategory, name="displayCategory"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("addToWatchlist/<int:id>", views.addToWatchlist, name="addToWatchlist"),
    path("removeFromWatchlist/<int:id>", views.removeFromWatchlist, name="removeFromWatchlist"),
    path("watchlist", views.displayWatchlist, name="watchlist"),
    path("addComment/<int:id>", views.addComment, name="addComment")
]
