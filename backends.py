from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import CustomUser

class CustomUserAdminAuthBackend(BaseBackend):
    """This is Authentication backend for admins"""
    def authenticate(self, request, username=None, password=None):
        try:
            user = get_object_or_404(CustomUser, username=username)
            password_valid = user.check_password(password)
            if password_valid and user.is_staff:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        except():
            return None

        return None

    def get_user(self, username):
        try:
            user = CustomUser.objects.get(username=username)
            if user:
                return user

        except ObjectDoesNotExist:
            return None

class CustomUserAuthBackend(BaseBackend):
    """This one is for simple users"""
    def authenticate(self, request, username=None, password=None):
        try:
            user = CustomUser.objects.get(username = username)

            if user.check_password(password):
                print('password matches!')

                return user
            else:
                raise ValidationError('Invalid Password')

        except ObjectDoesNotExist:
            raise Http404()

    def get_user(self, username):
        try:
            user = CustomUser.objects.get(username=username)
            if user:
                return user

        except ObjectDoesNotExist:
            return None
