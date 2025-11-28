from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Roles(models.TextChoices):
    CLIENT = 'CLIENT', _('Client')
    ADMIN = 'ADMIN', _('Admin')

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Ensure role is ADMIN for superusers
        extra_fields.setdefault('role', Roles.ADMIN)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True)  # optional
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    fullname = models.CharField(max_length=61, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.CLIENT)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.fullname = f"{self.first_name} {self.last_name}"
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if User.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError({'email': _('A user with this email already exists.')})

    def __str__(self):
        return f"{self.fullname} ({self.email})"

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
