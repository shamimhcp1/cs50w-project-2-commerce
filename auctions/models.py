from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"
    
class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    # store the highest bidder
    highest_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bids')

    # Watchlist feature
    watchers = models.ManyToManyField(User, related_name='watchlist', blank=True)

    # Indicates if the listing is closed
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}, {self.starting_bid}"

    def close_auction(self):
        if not self.is_closed:
            # Mark the listing as closed
            self.is_closed = True
            # If there are bids, set the highest bidder as the winner
            highest_bid = self.bids.order_by('-bid_amount').first()
            if highest_bid:
                self.highest_bidder = highest_bid.bidder
            else:
                # If there are no bids, set the seller as the winner
                self.highest_bidder = self.seller
            self.save()

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Bid on {self.listing.title} by {self.bidder.username}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment on {self.listing.title} by {self.commenter.username}, Date: {self.created_date}"