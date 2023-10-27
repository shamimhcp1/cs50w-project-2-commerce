from django.contrib import admin
from .models import Category, User, Bid, Listing

# Register your models here.
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Listing)
