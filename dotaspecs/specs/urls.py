from django.urls import path, include

from . import views
from .views import *

urlpatterns = [
    path('addpage/', create_post, name="add_page"),
    path('login/', user_login, name="login"),
    path('logout/', user_logout, name="logout"),
    path('register/', RegisterUser.as_view(), name="register"),
    path('post/<slug:post_slug>/', ShowPost.as_view(), name="post"),
    path('category/<slug:cat_slug>/', SpecsCategory.as_view(), name="category"),
    path('tag/<str:tag>/', SpecsTags.as_view(), name="specs_by_tags"),
    path('profile/', profile, name="profile"),
    # path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('password-reset/', UserForgotPasswordView.as_view(), name='password_reset'),
    path('set-new-password/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]