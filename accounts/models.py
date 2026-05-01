# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ('customer', 'Customer'),
#         ('admin', 'Admin'),
#     )

#     # Remove username field and use email as login
#     username = None
#     email = models.EmailField(unique=True, max_length=255)

#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
#     full_name = models.CharField(max_length=255)
#     address = models.TextField(blank=True, null=True)
#     phone = models.CharField(max_length=15, blank=True, null=True)

#     USERNAME_FIELD = 'email'      # Login using email
#     REQUIRED_FIELDS = ['full_name']   # Required when creating superuser

#     def __str__(self):
#         return f"{self.full_name} ({self.email})"

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, full_name, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )

    username = None
    email = models.EmailField(unique=True, max_length=255)

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    full_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.email})"