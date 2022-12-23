import time
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Post, Category, User, PostCategory, Author
from django.contrib.auth.models import Group
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .signals import *
from .tasks import notification


class PostList(ListView):
    model = Post
    ordering = 'time_in'
    template_name = 'news.html'
    context_object_name = 'posts'

    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        #проверка того, что юзер не подписан на данный раздел новостей
        if self.request.user.is_authenticated and ('category' in self.request.GET) and (self.request.GET['category'] != ''):
            subscriber = User.objects.get(username=self.request.user)
            if not subscriber.category_set.filter(pk=self.request.GET['category']):
                context['is_not_subscribe'] = True
                context['is_subscribe'] = False
            else:
                context['is_not_subscribe'] = False
                context['is_subscribe'] = True

        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):

        post = form.save(commit=False)
        f_path = self.request.get_full_path()
        if 'news' in f_path:
            post.post_category='news'
        else:
            post.post_category='post'
        #добавляю текущего автора при создании новости
        post.author = User.objects.get(username=self.request.user).author

        user_p = Post.objects.filter(time_in__gt=datetime.now().date(),author=User.objects.get(username=self.request.user).author)
        if len(user_p) >= 3:
            return redirect("post_count")

        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post')
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class PostCount(TemplateView):
    template_name = 'post_counter.html'


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context


@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
        Author.objects.create(username=User.objects.get(username=user))
    return redirect('/')
#обработка нажатия кнопки подписка

@login_required
def subscribe_me(request):
    user = request.user
    category = request.POST['cat']
    subscriber = User.objects.get(username=user)
    if not subscriber.category_set.filter(pk=category):
        subscriber.category_set.add(Category.objects.get(pk=category))

    return redirect('/portal/')

@login_required
def notsubscribe_me(request):
    user = request.user
    category = request.POST['cat']
    subscriber = User.objects.get(username=user)
    if subscriber.category_set.filter(pk=category):
        subscriber.category_set.remove(Category.objects.get(pk=category))

    return redirect('/portal/')

