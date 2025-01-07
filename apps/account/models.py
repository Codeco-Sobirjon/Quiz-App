from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from apps.account.managers.custom_user import CustomUserManager
from django.utils.translation import gettext as _


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=15, unique=True, verbose_name="Телефон")
    username = models.CharField(max_length=100, unique=True, verbose_name="Логин")
    full_name = models.CharField(max_length=100, verbose_name="ФИО")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

