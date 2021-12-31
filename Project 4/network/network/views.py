import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from itertools import chain

from .models import User, Post, Follow, Like


@csrf_exempt
def index(request):

    # Post.objects.all().delete()
    # User.objects.all().delete()
    # Like.objects.all().delete()
    # Follow.objects.all().delete()

    # get all posts in order from newest to oldest
    all_posts = Post.objects.all().order_by('-timestamp')

    # backend pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(all_posts, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if request.user.is_authenticated:
        # user's liked posts
        likes = Post.objects.filter(post__liker=request.user)
    else:
        likes = []

    return render(request, "network/index.html", {
        "user": request.user,
        "posts": posts,
        "likes": likes
    })


@csrf_exempt
@login_required
def new_post(request):

    # must create a new post by POST method
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # get content of post
    content = json.loads(request.body).get("body")
    if content == "":
        return JsonResponse({"error": "Post is blank."}, status=400)

    # create new post
    post = Post(content=content, user=request.user)
    post.save()

    return JsonResponse({"message": "Post created successfully."}, status=201)


@csrf_exempt
@login_required
def edit_post(request, postID):

    # editing post must be via POST method
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    # get edited content of post & post object
    content = json.loads(request.body).get("body")
    post = Post.objects.get(id=postID)
    
    # compare edited post with current post
    if post.content == content:
        return JsonResponse({"message": "No change was detected."}, status=201)
    
    # save new post content
    post.content = content
    post.save()

    return JsonResponse({"message": "Post edited successfully."}, status=201)


@csrf_exempt
@login_required
def like_post(request, postID):

    # get action (like or unlike) and post object
    action = json.loads(request.body).get("action")
    post = Post.objects.get(id=postID)
    
    if action == 'like':
        # increment post's likes
        post.likes += 1

        # create new Like object
        like = Like(post=post, liker=request.user)
        like.save()

    else:
        # decrement post's likes
        post.likes -= 1

        # remove existing Like object
        Like.objects.get(post=post, liker=request.user).delete()

    post.save()

    return JsonResponse({"message": "Success!", "likes": post.likes}, status=201)


@csrf_exempt
@login_required
def liked(request, postID):

    # return whether current logged-in user has liked the post
    post = Post.objects.get(id=postID)
    try:
        Like.objects.get(post=post, liker=request.user)
        return JsonResponse({"message": "Post is liked by user", "liked": True}, status=201)

    except ObjectDoesNotExist:
        return JsonResponse({"message": "Post is not liked by user", "liked": False}, status=201)


@csrf_exempt
def profile(request, username):

    # users
    user = User.objects.filter(username=request.user.username) # logged in user (can't just put request.user because getting is_following will throw an error)
    profile_user = User.objects.filter(username=username)

    # whether logged in user is following user of this profile
    is_following = Follow.objects.filter(followee__in=profile_user, follower__in=user)

    # GET request loads profile page
    if request.method == "GET":
        # get required user profile followers, following, and posts
        followers = Follow.objects.filter(followee__in=profile_user).count()
        following = Follow.objects.filter(follower__in=profile_user).count()
        all_posts = Post.objects.filter(user__in=profile_user).order_by('-timestamp')

        # backend pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(all_posts, 10)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        return render(request, "network/profile.html", {
            "user": request.user,
            "username": username,
            "followers": followers,
            "following": following,
            "is_following": is_following,
            "posts": posts
        })

    # POST request for 'follow/unfollow' button
    else:
        profile_user = get_object_or_404(User, username=username)   # User instance

        if is_following:
            # unfollow
            Follow.objects.filter(follower=request.user, followee=profile_user).delete()
        else:
            # follow
            follow = Follow(follower=request.user, followee=profile_user)
            follow.save()

        return HttpResponseRedirect(reverse("profile", kwargs={"username": username}))


@login_required
@csrf_exempt
def following(request, username):

    # get posts of accounts which the logged in user is following
    following_posts = []
    following = Follow.objects.filter(follower=request.user)
    for user in following:
        following_posts = list(chain(following_posts, Post.objects.filter(user=user.followee).order_by('-timestamp')))

    # backend pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(following_posts, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    return render(request, "network/following.html", {
        "user": request.user,
        "posts": posts
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
