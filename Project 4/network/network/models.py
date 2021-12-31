from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import related


class User(AbstractUser):
    pass


class Post(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=CASCADE, related_name="follower")
    followee = models.ForeignKey(User, on_delete=CASCADE, related_name="followee")


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=CASCADE, related_name="post")
    liker = models.ForeignKey(User, on_delete=CASCADE, related_name="liker")
