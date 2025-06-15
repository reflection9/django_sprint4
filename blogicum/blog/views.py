from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (ListView, DetailView, UpdateView,
                                  CreateView, DeleteView)

from .forms import PostForm, CommentForm
from .models import Post, Category, Comment
from .utils import filter_published_posts

# Create your views here.

User = get_user_model()


class PostPaginationMixin:
    """Миксин для постов."""

    model = Post
    paginate_by = 10


class PostCRUDMixin(LoginRequiredMixin):
    """Миксин для CRUD постов."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostAccessMixin(LoginRequiredMixin):
    """Миксин доступа к постам."""

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user != post.author:
            return redirect('blog:post_detail', pk=post.pk)
        return super().dispatch(request, *args, **kwargs)


class CommentEditingMixin(LoginRequiredMixin):
    """Миксин для изменения данных в комментариях."""

    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect('blog:post_detail', pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


class CommentCRUDMixin(LoginRequiredMixin):
    """Миксин для CRUD комментариев."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'


class IndexListView(PostPaginationMixin, ListView):
    """Обработка запроса для передачи списка постов"""

    queryset = filter_published_posts(
        Post.objects.select_related('category').all())
    template_name = 'blog/index.html'
    context_object_name = 'post_list'


class PostDetailView(DetailView):
    """Обрабатывает запрос по адресу posts/<int:id>/"""

    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        if ((post.pub_date > timezone.now() or not post.is_published
             or (post.category and not post.category.is_published))
                and not post.author == self.request.user):
            raise Http404("Публикация недоступна.")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            Comment.objects.filter(post=self.get_object())
        )
        return context


class CategoryListView(PostPaginationMixin, ListView):
    """Обрабатывает запрос по адресу category/<slug:category_slug>/"""

    template_name = 'blog/category.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(Category, slug=category_slug,
                                     is_published=True)
        return filter_published_posts(
            category.post_categories.select_related('category').all())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        context['category'] = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        return context


class ProfileListView(ListView):
    """Профиль пользователя."""

    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        self.profile = get_object_or_404(User,
                                         username=self.kwargs.get('username'))
        posts = Post.objects.filter(author_id=self.profile.id)
        if self.profile.id != self.request.user.id:
            posts = filter_published_posts(posts)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context
    # TODO: убрать комментарии в profile.html


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    model = User
    template_name = 'blog/user.html'
    fields = ['username', 'email', 'first_name', 'last_name']

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostCreateView(PostCRUDMixin, CreateView):
    """Создание поста."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(PostCRUDMixin, PostAccessMixin, UpdateView):
    """Редактирование поста."""

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('pk')}
        )


class PostDeleteView(PostCRUDMixin, PostAccessMixin, DeleteView):
    """Удаление поста."""

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return post

    def get_success_url(self):
        return reverse('blog:index')


class CommentCreateView(CommentCRUDMixin, CreateView):
    """Создание комментария."""

    def get_queryset(self):
        return Comment.objects.filter(post=self.kwargs['post'])

    def dispatch(self, request, *args, **kwargs):
        self.publication = get_object_or_404(Post, pk=kwargs['post'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.publication
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post']}
        )


class CommentUpdateView(CommentCRUDMixin, CommentEditingMixin, UpdateView):
    """Изменение комментария."""


class CommentDeleteView(CommentCRUDMixin, CommentEditingMixin, DeleteView):
    """Удаление комментария."""
