from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout, login, authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView, ListView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext

from .models import Post
from memberships.models import UserMembership
from memberships.views import get_user_membership
from comments.forms import CommentForm
from comments.models import Comment
from .forms import PostModelForm, NewsLetterSignUpForm


def search_list_view(request):
    search_query = request.GET.get('search')
    search_results = UserMembership.objects.filter(user__username__icontains=search_query)

    return render(request, 'blog/posts_list.html', {'search_results': search_results})

"""
- Query all posts ordered by reversing the order of the timestamp
so most recent posts show up first.
- Query all posts to be filtered by title using Django's search tool
- Using Paginator, create a new page for every 3 posts.
- For recent posts, show 3 most recent
"""
def posts_list(request):
    queryset_list = Post.objects.all().order_by("-timestamp")
    users = UserMembership.objects.exclude(user=request.user)
    query = request.GET.get('q')
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query)
            ).distinct()
    paginator = Paginator(queryset_list, 3)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    # get the last 3 posts
    recent_posts = Post.objects.order_by('-timestamp')[0:3]

    context = {
        'users': users,
        'all_posts': queryset,
        'page_request_var': page_request_var,
        'recent_posts': recent_posts
    }
    return render(request, 'blog/posts_list.html', context)

"""
Get the user and the specific post by slug.
Initialize comments object by "post" content type and the ID
Pass in form with the initial data
Execute comment form and clean data
Determine comments parent child relation
Create comment
"""
def post_detail(request, slug=None):
    user = UserMembership.objects.filter(user=request.user)[0]
    instance = get_object_or_404(Post, slug=slug)
    # ContentType.objects.get_for_model(Post)
    # obj_id = instance_id
    # comments = Comments.objects.filter(content_type=content_type, object_id=obj_id)
    initial_data = {
        "content_type": instance.get_content_type, # Property on Model
        "object_id": instance.id # POST OBJECT ID
    }
    print(initial_data)
    form = CommentForm(request.POST or None, initial=initial_data)
    if form.is_valid():
        c_type = form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type) # gets from model class
        obj_id = form.cleaned_data.get("object_id")
        content_data = form.cleaned_data.get("content")
        parent_obj = None
        try: # make sure parent_id exists in DB
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None # parent is None by default

        if parent_id: # does parent QS exist?
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()

        new_comment, created = Comment.objects.get_or_create(
            user = request.user,
            content_type = content_type,
            object_id = obj_id,
            content = content_data,
            parent = parent_obj,
        )
        # re render post detail page after comment
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    comments = instance.comments # property on Post Model
    context = {
        'auth_user': user,
        'instance': instance,
        'comments': comments,
        'comment_form': form,
    }
    return render(request, 'blog/posts_detail.html', context)


class PostLikeToggle(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        obj = get_object_or_404(Post, slug=slug)
        url_ = obj.get_absolute_url()
        user = obj.author
        if user:
            if user in obj.likes.all():
                obj.likes.remove(user)
            else:
                obj.likes.add(user)
        return url_


class PostLikeAPIToggle(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, slug=None, format=None):
        # slug = self.kwargs.get('slug')
        obj = get_object_or_404(Post, slug=slug)
        url_ = obj.get_absolute_url()
        user = get_user_membership(request)
        updated = False
        liked = False
        if user.user.is_authenticated:
            if user in obj.likes.all():
                liked = False
                updated = True
                obj.likes.remove(user)
            else:
                liked = True
                obj.likes.add(user)
                updated = True
        data = {
            "updated": updated,
            "liked": liked
        }

        return Response(data)

"""
Allows a user to create a post. Connects user/user membership to
author of a blog post.
"""
@login_required
def post_create(request):
    form = PostModelForm()
    if request.POST:
        form = PostModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = get_user_membership(request)
            form.instance.save()
        post = get_object_or_404(Post, slug=form.instance.slug)
        return redirect(post.get_absolute_url())

    context = {'form': form}
    return render(request, "blog/create_post.html", context)



def post_update(request, slug):
	unique_post = get_object_or_404(Post, slug=slug)
	form = PostModelForm(request.POST or None,
						request.FILES or None,
						instance=unique_post)
	if form.is_valid():
		form.save()
		return redirect('/blog/')

	context = {
		'form': form
	}
	return render(request, "blog/create_post.html", context)


def post_delete(request, slug):
    unique_post = get_object_or_404(Post, slug=slug)
    unique_post.delete()
    return redirect('blog:blog')


def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsLetterSignUpForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            if NewsLetterUser.objects.filter(email=instance.email).exists():
                messages.warning(request, 'Your email already exists.')
            else:
                instance.save()
    else:

        form = NewsLetterSignUpForm()

        return render(request, 'blog/posts_list.html', {'form': form})

def newsletter_unsubscribe(request):
    form = NewsLetterSignUpForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        if NewsLetterUser.objects.filter(email=instance.email).exists():
            NewsLetterUser.objects.filter(email.instance.email).delete()
        else:
            print('Sorry, we did not find your email address.')

        context = {
            'form': form
        }
        template = 'blog/unsubscribe.html'
        return render(request, template, context)