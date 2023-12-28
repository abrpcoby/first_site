import operator
from functools import reduce

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, JsonResponse, \
    StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.contrib.auth import get_user_model
from taggit.models import Tag
from django.shortcuts import render


# tags_all = Tag.objects.all()
User = get_user_model()

from .forms import *
from .models import *

menu = [{'title': "Предложить", 'url_name': 'add_page'},
        ]


class IndexView(ListView):
    model = Specs
    template_name = "specs/index.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        context['title'] = 'Главная страница'
        context['cat_selected'] = 0
        context['all_posts'] = Specs.objects.filter(is_published=True)
        return context

    def get_queryset(self):

        search_query = self.request.GET.get('search', '')

        if search_query:
            posts = Specs.objects.filter(Q(title__iregex=search_query) | Q(author__iregex=search_query),
                                         is_published=True).select_related('cat', 'moderator_nickname').\
                prefetch_related('tags')
        else:
            posts = Specs.objects.filter(is_published=True).\
                select_related('cat', 'moderator_nickname').prefetch_related('tags')
        return posts


class RegisterUser(CreateView):
    form_class = RegistrationForm
    template_name = 'specs/register.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        context['title'] = 'Регистрация'
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')


# def registerUser(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             return redirect('home')
#         else:
#             form = RegistrationForm(request.POST)
#             context = {
#                 'form': form
#             }
#         return render(request, 'specs/register.html', context)
#     return render(request, 'specs/register.html', {'form': RegistrationForm()})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('home'))
    else:
        form = UserLoginForm()

    context = {
        'form': form,
        'menu': menu,
        'title': 'Авторизация',
    }
    return render(request, 'specs/login.html', context)


def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if request.method == 'POST':
            form = UserProfileForm(instance=request.user, data=request.POST, files=request.FILES)

            if form.is_valid():
                form.save()
                messages.success(request, 'Изменения сохранены')
                return HttpResponseRedirect(reverse('profile'))
        else:
            form = UserProfileForm(instance=request.user)
        context = {
            'title': 'DotaSpecs - Профиль пользователя',
            'form': form,
            'menu': menu,
        }
        return render(request, 'specs/profile.html', context)


def user_logout(request):
    logout(request)
    return redirect('home')


class ShowPost(DetailView):
    model = Specs
    template_name = 'specs/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        context['title'] = context['post']
        return context


class SpecsTags(ListView):
    model = Specs
    template_name = "specs/index.html"
    context_object_name = "posts"
    paginate_by = 5
    tag = None

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['tag'])
        queryset = Specs.objects.all().filter(tags__slug=self.tag.slug, is_published=True).\
            select_related('cat', 'moderator_nickname').prefetch_related('tags')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        context['title'] = f'Результаты по тегу: {self.tag.name}'
        context['queryset'] = Specs.objects.all().filter(tags__slug=self.tag.slug, is_published=True)
        context['tag'] = Tag.objects.get(slug=self.kwargs['tag'])
        return context


class SpecsCategory(ListView):
    model = Specs
    template_name = "specs/index.html"
    context_object_name = "posts"
    paginate_by = 5
    allow_empty = False

    def get_queryset(self):
        return Specs.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).\
            select_related('cat', 'moderator_nickname').prefetch_related('tags')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        context['menu'] = menu
        context['title'] = 'Категория - ' + str(c.name)
        context['cat_selected'] = c.pk
        context['cats_all'] = Specs.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True)
        context['cat_name'] = str(c.name)
        return context


# @method_decorator(login_required, name='dispatch')
# class AddPage(CreateView):
#     form_class = AddPostForm
#     template_name = 'specs/addpage.html'
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['menu'] = menu
#         context['title'] = 'Предложить'
#         return context
#
#     def form_valid(self, form):
#         AddSpec.objects.create(**form.cleaned_data)
#         return redirect('home')


@login_required
def create_post(request):
    data = request.POST.copy()
    data.update({'nickname': request.user})
    form = AddPostForm(data)
    if form.is_valid():
        form.nickname = request.user
        form.save()
        messages.success(request, 'Ваше предложение отправлено и будет рассмотрено администрацией'
                                  ' в ближайшее время')
        return redirect('home')
    else:
        form = AddPostForm()
    return render(request, 'specs/addpage.html', {'form': form, 'title': 'Предложить', 'menu': menu})


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    """
    Представление по сбросу пароля по почте
    """
    form_class = UserForgotPasswordForm
    template_name = 'specs/user_password_reset.html'
    success_url = reverse_lazy('home')
    success_message = 'Вам на почту отправлено письмо с дальнейшей инструкцией по сбросу пароля. ' \
                      'Не забудьте проверить папку "Спам"'

    subject_template_name = 'specs/email/password_subject_reset_mail.txt'
    email_template_name = 'specs/email/password_reset_mail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Восстановление пароля'
        context['menu'] = menu
        return context


class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    """
    Представление установки нового пароля
    """
    form_class = UserSetNewPasswordForm
    template_name = 'specs/user_password_set_new.html'
    success_url = reverse_lazy('home')
    success_message = 'Пароль успешно изменен. Теперь вы можете авторизоваться'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Восстановление пароля'
        context['menu'] = menu
        return context

# def show_post(request, post_slug):
#     post = get_object_or_404(Specs, slug=post_slug)
#
#     context = {
#         'post': post,
#         'menu': menu,
#         'title': post.title,
#         'cat_selected': post.cat_id,
#     }
#
#     return render(request, 'specs/post.html', context=context)


# def show_category(request, cat_slug):
#     posts = Specs.objects.filter(cat__slug=cat_slug)
#     paginator = Paginator(posts, 1000)
#
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#
#     if len(posts) == 0:
#         raise Http404()
#
#     context = {
#         'page_obj': page_obj,
#         'posts': posts,
#         'menu': menu,
#         'title': 'Отображение по категориям',
#         'cat_selected': cat_slug,
#     }
#
#     return render(request, 'specs/index.html', context=context)

# def index(request):
#     search_query = request.GET.get('search', '')
#
#     if search_query:
#         posts = Specs.objects.filter(Q(title__iregex=search_query))
#     else:
#         posts = Specs.objects.all()
#
#     paginator = Paginator(posts, 10)
#
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#
#     context = {
#         'page_obj': page_obj,
#         'posts': posts,
#         'menu': menu,
#         'title': 'Главная страница',
#         'cat_selected': 0,
#     }
#
#     return render(request, 'specs/index.html', context=context)


# def addpage(request):
#     if request.method == 'POST':
#         form = AddPostForm(request.POST, request.FILES)
#
#         if form.is_valid():
#             print(form.cleaned_data)
#             try:
#                 AddSpec.objects.create(**form.cleaned_data)
#                 return redirect('home')
#             except:
#                 form.add_error(None, 'Ошибка, проверьте, выбрана ли категория.')
#     else:
#         form = AddPostForm()
#
#     return render(request, 'specs/addpage.html', {'form': form, 'menu': menu, 'title': 'Предложить'})

# class Search(ListView):
#     template_name = "specs/index.html"
#     context_object_name = "search"
#
#     def get_queryset(self):
#         return Specs.objects.filter(title__iregex=self.request.GET.get('search'))
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['menu'] = menu
#         context['search'] = self.request.GET.get('search')
#         return context

# def search(request):
#     search_query = request.GET.get('search', '')
#
#     if search_query:
#         posts = Specs.objects.filter(Q(title__iregex=search_query))
#     else:
#         posts = Specs.objects.all()
#
#
#
#     context = {
#         'posts': posts,
#         'menu': menu,
#         'title': 'Главная страница',
#         'cat_selected': 0,
#     }
#
#     return render(request, 'specs/index.html', context=context)
