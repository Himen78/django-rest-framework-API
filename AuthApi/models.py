from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from rest_framework.authtoken.models import Token
import binascii
from django.utils.translation import ugettext_lazy as _
from datetime import date
from django.conf import settings
import os, time

# Create your models here.

class UserToken(models.Model):

    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"),
            related_name='auth_tokens', on_delete=models.CASCADE) #  CASCADE SQL Standard : When the referenced object is deleted, also delete the objects that have references to it
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = _("Token") # human-readable name for the object
        verbose_name_plural = _("Tokens") # _ is marked as translated string based on machine language.
        ordering = ('-created_at',) # - Prefix, indicate the decending order OR without added - will be ordered by ascending

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(UserToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode() # Return the hexadecimal representation of binary data. Byte converted into 2-digit hex representation.

    def __str__(self):
        return self.key


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("User must have an email address")
        if not password:
            raise ValueError("User must have a password")

        user_obj = self.model(
            email = self.normalize_email(email)  # normalize email is built in method for BaseUserManager class.
        )
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_user(self, email, password=None, **extra_fields):

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_Superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        
        user =  self._create_user(email, password, **extra_fields)
        user.is_staff=True
        user.is_superuser=True
        user.save()
        return user

class User(AbstractUser):

    email = models.EmailField(max_length=40, unique=True)
    username = models.CharField(blank=True, null=True, max_length=32)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    
    objects = UserManager()