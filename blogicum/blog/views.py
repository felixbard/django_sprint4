# blog/views.py
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from blog.models import Post, Category, Comment, User
from .forms import PostForm, ProfileForm, CommentForm
from django.views.generic import (
    ListView,
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from typing import Any
from django.db.models import Count


POSTS_ON_PAGE = 10


def get_published_posts(posts, flag=True):
    queryset = posts.prefetch_related('comments').select_related(
        'category',
        'author',
        'location',
    )
    if flag:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )

    return queryset.annotate(comment_count=Count('comments')).order_by(
        Post._meta.ordering[0]
    )


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        return get_published_posts(Post.objects)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    paginate_by = POSTS_ON_PAGE
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author:
            post = get_object_or_404(
                get_published_posts(Post.objects),
                pk=self.kwargs[self.pk_url_kwarg],
            )
        return post

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            form=CommentForm(),
            comments=self.object.comments.select_related('author'),
        )


class CategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_ON_PAGE
    pk_url_kwarg = 'category_slug'

    def get_queryset(self):
        return get_published_posts(
            get_object_or_404(
                Category, is_published=True,
                slug=self.kwargs[self.pk_url_kwarg]
            ).posts
        )


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    queryset = Post.objects.all()
    paginate_by = POSTS_ON_PAGE

    def get_user(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        return get_published_posts(
            self.get_user().posts, flag=(self.request.user != self.get_user())
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return dict(**super().get_context_data(**kwargs),
                    profile=self.get_user())


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = ProfileForm

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.get(username=self.request.user.username)

    def get_success_url(self):
        return reverse('blog:index')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateDeleteMixin:
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostUpdateDeleteMixin, LoginRequiredMixin, UpdateView):
    form_class = PostForm


class PostDeleteView(PostUpdateDeleteMixin, LoginRequiredMixin, DeleteView):

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return dict(
            **super().get_context_data(**kwargs),
            form=PostForm(instance=self.object),
        )

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class CommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs[self.pk_url_kwarg]])


class CommentUpdateDeleteMixin:
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self):
        comment = get_object_or_404(
            Comment, pk=self.kwargs['comment_id'], author=self.request.user
        )
        return comment

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class CommentUpdateView(CommentUpdateDeleteMixin,
                        LoginRequiredMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentUpdateDeleteMixin,
                        LoginRequiredMixin, DeleteView):
    ...
