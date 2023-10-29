from django.urls import path

from . import views

urlpatterns = [
    # index
    path("", views.index, name="index"),

    # login or register
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # listing
    path("create_listing", views.create_listing, name="create_listing"),
    path("listings/<int:listing_id>", views.single_listing, name="single_listing"),
    path("seller/<int:seller_id>", views.listing_by_seller, name="listing_by_seller"),
    path("my_listing", views.my_listing, name="my_listing"),
    path("edit_listing/<int:listing_id>", views.edit_listing, name="edit_listing"),

    # category
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.single_category, name="single_category"),
    path("no-category", views.no_category, name="no_category"),
]
