from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage


# Create a new user
class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)

        user.save()

        return user

    # Use this to create a super user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "Admin")

        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=45, null=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('Admin', 'Admin'),
            ('ProjectManager', 'ProjectManager'),
            ('Engineer', 'Engineer'),
        ],
        default='Engineer',
    )
    image = models.ImageField(upload_to='user_image/', storage=MediaCloudinaryStorage())
    engineer_details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        ordering = ("-created_at",)
