from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _prepare_user(self, email, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        return self.model(email=email, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        user = self._prepare_user(email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user_without_password(self, email, **extra_fields):
        user = self._prepare_user(email, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        """
        Gets user for username with case insensitive email.
        """
        return self.get(email__iexact=username)


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    needs_change_password = models.BooleanField(default=False)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def set_password(self, raw_password, needs_change_password=False):
        super(User, self).set_password(raw_password)
        self.needs_change_password = needs_change_password

    def force_new_password(self, raw_password):
        self.set_password(raw_password, needs_change_password=True)
