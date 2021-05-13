from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    user = models.ForeignKey(User, related_name="listings", on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)
    CATEGORY_CHOICES = [
        ('N', 'None'), ('E', 'Electronics'), ('CT', 'Computers & Tablets'), ('F', 'Fashion'), ('A', 'Accessories'),
        ('TH', 'Toys & Hobbies'), ('HG', 'Home & Garden'), ('C', 'Collectibles'), ('O', 'Others')
    ]
    category = models.CharField(max_length=19, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='listing_images', null=True)

    current_price = models.DecimalField(max_digits=11, decimal_places=2, null=True)

    watchers = models.ManyToManyField(User, related_name="watchlist")
    closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} in {self.category} listed by {self.user}, ${self.price}. {self.description}. Closed: {self.closed}"
        

class Bid(models.Model):
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    listing = models.ForeignKey(Listing, related_name="bids", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="bids", on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} bid on item '{self.listing.name}' by {self.user}"


class Comment(models.Model):
    comment = models.TextField()
    listing = models.ForeignKey(Listing, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"'{self.comment}' -{self.user} on {self.listing}"
