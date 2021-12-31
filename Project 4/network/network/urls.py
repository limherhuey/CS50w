
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API routes
    path("posts", views.new_post, name="post"),
    path("edit/<int:postID>", views.edit_post, name="edit"),
    path("like/<int:postID>", views.like_post, name="like"),
    path("liked/<int:postID>", views.liked, name="liked"),

    # other views
    path("profile/<str:username>", views.profile, name="profile"),
    path("<str:username>/following", views.following, name="following"),
]
