from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.core.files.base import ContentFile
import requests
from django import forms

from .models import User, Listing, Bid, Comment


# form for creating a new listing
class CreateListing(forms.Form):
    name = forms.CharField(label="Name", max_length=80, widget=forms.TextInput(attrs={'class': 'field'}))
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={'class': 'field', 'rows': 3, 'cols': 150}), max_length=1000)
    price = forms.DecimalField(label="Starting Bid", min_value=0, max_digits=11, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'field'}))
    category = forms.ChoiceField(label="Category", choices=Listing.CATEGORY_CHOICES, required=False, widget=forms.Select(attrs={'class': 'field'}))
    image = forms.URLField(label="Image URL", required=False, widget=forms.URLInput(attrs={'class': 'field'}))


# form for bidding
class NewBid(forms.Form):
    def __init__(self, *args, **kwargs):
        self.min = kwargs.pop('current_price')
        super(NewBid, self).__init__(*args, **kwargs)
        
        # set minimum value for bidding
        self.fields['bid'].widget.attrs.update({'min': self.min})
    
    bid = forms.DecimalField(label='', max_digits=11, decimal_places=2, widget=forms.NumberInput(attrs={'id': 'bidform'}))


def index(request):
    # update current price of all listings to its highest bid or original price if no bids
    for listing in Listing.objects.exclude(closed=True):
        try:
            listing.current_price = Bid.objects.filter(listing=listing).latest('datetime').amount
        except Bid.DoesNotExist:
            listing.current_price = listing.price
        listing.save(update_fields=["current_price"])

    return render(request, "auctions/index.html", {
        "listings": Listing.objects.exclude(closed=True)
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


@login_required
def list(request):
    if request.method == "POST":

        form = CreateListing(request.POST)
        if form.is_valid():
            # get contents of form if it is valid (and logged-in user)
            user = request.user
            name = form.cleaned_data["name"]
            price = form.cleaned_data["price"]
            category = form.cleaned_data["category"]
            description = form.cleaned_data["description"]

            # create and save new listing
            l = Listing(user=user, name=name, price=price, current_price=price, category=category, description=description)
            l.save()
            
            # save image of listing
            image_url = form.cleaned_data["image"]
            if image_url:
                image_content = ContentFile(requests.get(image_url).content)
                l.image.save("listing_%d.png" % l.pk, image_content)
            
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/list.html", {
            "form": CreateListing()
        })


def listing_page(request, pk):
    if request.method == "POST":

        listing = Listing.objects.get(pk=pk)
        user = request.user

        if request.POST.get("buttons", False):
            creator = request.POST.get("creator", False)
            watcher = request.POST.get("watcher", False)
            
            # for user who listed the item: close auction
            if creator == "close":
                listing.closed = True
                listing.save(update_fields=["closed"])
                
            # for all other users: watch / unwatch
            if watcher == "watch":
                listing.watchers.add(user)
            elif watcher == "unwatch":
                listing.watchers.remove(user)

        # for all other users: bidding
        elif request.POST.get("place_bid", False):
            amount = request.POST["bid"]
            bid = Bid(amount=amount, user=user, listing=listing)
            bid.save()
        
        # for all users: commenting
        else:
            comment = request.POST["comment"]
            if comment:
                c = Comment(comment=comment, user=user, listing=listing)
                c.save()

        return HttpResponseRedirect(reverse("listing_page", kwargs={'pk': pk}))

    else:
        try:
            listing = Listing.objects.get(pk=pk)
            user = request.user
        except Listing.DoesNotExist:
            raise Http404("Listing not found.")

        # get current price (highest bid or original price if there are no bids)
        try:
            bid = Bid.objects.filter(listing=listing).latest('datetime')
            current_price = bid.amount
            winner = bid.user
        except Bid.DoesNotExist:
            current_price = listing.price
            winner = None

        bid_form = NewBid(current_price=current_price)
        comments = Comment.objects.filter(listing=listing)

        return render(request, "auctions/listing.html", {
            "user": user,
            "listing": listing,
            "current_price": current_price,
            "winner": winner,
            "bid_form": bid_form,
            "comments": comments
        })


@login_required
def watchlist(request, username):
    user = User.objects.get(username=username)
    watching = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watching
    })
    

def categories(request, category):
    if category == 'list':
        return render(request, "auctions/categories.html", {
            "categories": Listing.CATEGORY_CHOICES
        })
    else:
        listings = Listing.objects.filter(category=category).exclude(closed=True)
        # get the category's human readable name
        for cat in Listing.CATEGORY_CHOICES:
            if category in cat:
                category = cat[1]
                break

        return render(request, "auctions/categories.html", {
            "listings": listings,
            "category": category
        })
        