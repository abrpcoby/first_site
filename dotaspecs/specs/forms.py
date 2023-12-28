import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordResetForm, \
    SetPasswordForm
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q

from django.conf import settings
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from PIL import Image
from django.db.models.fields.files import ImageFieldFile

from .models import *


class AddPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat'].empty_label = "Не выбрана"
    nickname = forms.HiddenInput()
    content = forms.CharField(min_length=10, max_length=1000, widget=forms.Textarea(attrs={'placeholder': 'Текст',
                                                                                           'class': 'form-content'}))
    # video = forms.FileField(required=False, label="Видео или фото",
    #                         widget=forms.FileInput(attrs={'class': 'file input__file',
    #                                                       'id': 'input__file'}))
    cat = forms.ModelChoiceField(queryset=Category.objects.all(), label="Категория", required=False)
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, public_key=settings.RECAPTCHA_PUBLIC_KEY,
                               private_key=settings.RECAPTCHA_PRIVATE_KEY, label='ReCAPTCHA')

    class Meta:
        model = AddSpec
        fields = ("content", "nickname", "video", "cat")


# class LoginForm(forms.ModelForm): # Форма логина
#
#     password = forms.CharField(widget=forms.PasswordInput)
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['username'].label = 'Логин'
#         self.fields['password'].label = 'Пароль'
#
#     def clean(self):
#         username = self.cleaned_data['username']
#         password = self.cleaned_data['password']
#         if not User.objects.filter(username=username).exists():
#             raise forms.ValidationError(f"Пользователь с логином {username} не найден")
#         user = User.objects.filter(username=username).first()
#         if user:
#             if not user.check_password(password):
#                 raise forms.ValidationError("Неверный пароль")
#         return self.cleaned_data
#
#     class Meta:
#         model = User
#         fields = ['username', 'password']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text', 'placeholder': 'Логин или e-mail'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-text', 'placeholder': 'Пароль'}))
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, public_key=settings.RECAPTCHA_PUBLIC_KEY,
                               private_key=settings.RECAPTCHA_PRIVATE_KEY, label='ReCAPTCHA')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).exists():
            raise forms.ValidationError(f"Пользователь с логином {username} не найден")
        user = User.objects.filter((Q(username__iexact=username) | Q(email__iexact=username))).first()

        if user:
            if not user.check_password(password):
                raise forms.ValidationError("Неверный пароль")
            if not user.is_active:
                raise forms.ValidationError("Пользователь заблокирован")
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('username', 'password')


class RegistrationForm(forms.ModelForm):  # Форма регистрации

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-text', 'placeholder': 'Имя пользователя'}))
    confirm_password = forms.CharField \
        (widget=forms.PasswordInput(attrs={'class': 'input-text', 'placeholder': 'Повтор пароля'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input-text', 'placeholder': 'Пароль'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input-text', 'placeholder': 'E-mail'}))
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, public_key=settings.RECAPTCHA_PUBLIC_KEY,
                               private_key=settings.RECAPTCHA_PRIVATE_KEY, label='ReCAPTCHA')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
        self.fields['confirm_password'].label = 'Подтвердите пароль'
        self.fields['email'].label = 'Электронная почта'

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с такой электронной почтой уже зарегистрирован')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if not username.isdigit():
            if len(username) < 3:
                raise forms.ValidationError('Минимальная длина логина 3 символа')
            elif User.objects.filter(username=username).exists():
                raise forms.ValidationError(f'Имя {username} занято')
        else:
            raise forms.ValidationError(f'Никнейм не может состоять только из цифр.')
        return username

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if len(password) < 8 or len(password) > 64:
            self.add_error('password', 'Длина пароля не может быть меньше 8 символов и больше 64')
        elif password != confirm_password:
            self.add_error('password', 'Пароли не совпадают')
            self.add_error('confirm_password', 'Пароли не совпадают')
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email']


class UserProfileForm(UserChangeForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'custom-file-input',
        'name': 'file[]',
        'accept': "image/*",
        'id': 'userAvatar',
    }))

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'placeholder': 'Введите имя'}), required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'placeholder': 'Введите фамилию'}), required=False)

    def clean_image(self):
        image = self.cleaned_data.get('image', False)

        w, h = get_image_dimensions(image)
        min_width = min_height = 120
        if w <= min_width or h <= min_height:
            raise forms.ValidationError(f'Минимальный размер изображения: {min_width}px:{min_height}px')

        if image and isinstance(image, UploadedFile):
            main, sub = image.content_type.split('/')
            if not (main == 'image' and sub.lower() in ['jpeg', 'pjpeg', 'png', 'jpg', 'webp', 'rgba']):
                raise forms.ValidationError('Используйте формат jpeg, png или jpg')

            if len(image) > (1 * 1024 * 1024):
                raise forms.ValidationError('Максимальный вес изображения: 1 мб')

        elif image and isinstance(image, ImageFieldFile):
            pass

        return image

    def clean_email(self):
        email = self.cleaned_data['email']
        users = User.objects.exclude(pk=self.instance.pk).filter(email=email).exists()

        if users:
            raise forms.ValidationError('Адрес электронной почты занят')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']

        if not username.isdigit():
            users = User.objects.exclude(pk=self.instance.pk).filter(username=username).exists()
            if len(username) < 3:
                raise forms.ValidationError('Минимальная длина логина 3 символа')
            elif users:
                raise forms.ValidationError(f'Имя {username} занято')
        else:
            raise forms.ValidationError(f'Никнейм не может состоять только из цифр')
        return username

    class Meta:
        model = User
        fields = ('username', 'image', 'email', 'first_name', 'last_name')


class UserForgotPasswordForm(PasswordResetForm):
    """
    Запрос на восстановление пароля
    """
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, public_key=settings.RECAPTCHA_PUBLIC_KEY,
                               private_key=settings.RECAPTCHA_PRIVATE_KEY, label='ReCAPTCHA')

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control custom-form',
                'autocomplete': 'off'
            })


class UserSetNewPasswordForm(SetPasswordForm):
    """
    Изменение пароля пользователя после подтверждения
    """

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control custom-form',
                'autocomplete': 'off'
            })
