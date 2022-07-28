from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render, get_object_or_404, redirect
)
from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm


def paginator(request, post_list):
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    post_list = Post.objects.all()
    context = {'page_obj': paginator(request, post_list)}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
        'page_obj': paginator(request, post_list),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    if author.get_full_name():
        author_name = author.get_full_name()
    else:
        author_name = author.username
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author,
    ).exists()
    context = {
        'page_obj': paginator(request, post_list),
        'posts_count': post_list.count(),
        'author_name': author_name,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    if request.method == 'POST':
        author = Post(author=request.user)
        form = CommentForm(request.POST, instance=author)
        if form.is_valid():
            form.cleaned_data
            form.save()
    form = CommentForm()
    context = {
        'post': post,
        'posts_count': post.author.posts.count(),
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


is_edit = False


@login_required
def post_create(request):
    if request.method == 'POST':
        author = Post(author=request.user)
        form = PostForm(
            request.POST,
            files=request.FILES or None,
            instance=author,
        )
        if form.is_valid():
            form.cleaned_data
            form.save()
            return redirect('posts:profile', request.user.username)
        return render(
            request,
            'posts/post_create.html',
            {'form': form, 'is_edit': is_edit}
        )
    form = PostForm()
    return render(
        request,
        'posts/post_create.html',
        {'form': form, 'is_edit': is_edit}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.cleaned_data
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request,
        'posts/post_create.html',
        {'form': form, 'is_edit': is_edit}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': paginator(request, posts_list),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:follow_index')
