import datetime
import os
import pathlib
from django import dispatch
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin, UserManager
from django.db import models
from django.db.models import GenericIPAddressField, Q
from django.db.models.manager import BaseManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
#User and related models:
from transliterate import translit

from django.utils.translation import gettext as _
from datetime import date

profile_created = dispatch.Signal()
class CustomUserManager(BaseUserManager):

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('empty username')

        if not email:
            raise ValueError('empty email')

        if not password:
            raise ValueError('empty password')

        email = self.normalize_email(email)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_user(self, username, email, password):

        default_param_dict = {'is_blocked': False, 'is_confirmed': False, 'is_active': True,
        'is_superuser': True, 'avatar': settings.MEDIA_ROOT + '/default_ava.png', 'last_online': timezone.now()}

        if 'date_of_birth' not in default_param_dict.keys():
            default_param_dict.setdefault('date_of_birth', '2005-01-01')

        user = self._create_user(username=username, email=email, password=password, **default_param_dict)
        settings.ADMIN_LOGIN.append(user.username)

        profile_created.send(sender=self.create_user, instance=user, created=True)

        return user

    def create_superuser(self, username, email, password):

        default_admin_param_dict = {'is_superuser': True, 'is_staff': True,
        'is_admin': True, 'avatar': settings.MEDIA_ROOT + '/default_ava.png', 'last_online': timezone.now()}

        user = self._create_user(
            username=username,
            email=email, password=password, **default_admin_param_dict
        )

        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        
        user.save(using=self._db)

        return user

# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):

    genders = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]

#There starts user model fields:
    objects = CustomUserManager()

    username = models.CharField(verbose_name='Users name',

               unique=True,
               max_length=40, null=False, blank=False)

    gender = models.CharField(verbose_name='gender choice', max_length = 10,

               null=False,
               choices=genders,
               default=genders[0][0])

    ip_address = GenericIPAddressField(verbose_name='User IP Address', default='127.0.0.1')

    password = models.CharField(verbose_name='User password', null=False, blank=False, max_length=200)


    email = models.EmailField(verbose_name='User Email', null=False, unique=True)

    avatar = models.ImageField(verbose_name='User avatar', default = settings.MEDIA_ROOT + '/default_ava.png', null=True, blank=True)


    date_of_birth = models.DateField(verbose_name='Date of Birth', null=True, default=None)

    last_online = models.DateTimeField(verbose_name='Last Online', default = timezone.now())

    money_balance = models.PositiveIntegerField(verbose_name='Money Balance', default=100)


    is_staff = models.BooleanField(verbose_name='Is Staff', default=False)

    is_active = models.BooleanField(verbose_name='Is Active', default=True)

    is_blocked = models.BooleanField(verbose_name='Is User Blocked', default=False)

    is_confirmed = models.BooleanField(verbose_name='Is confirmed', default=False)

    is_superuser = models.BooleanField(verbose_name='Is Super User', default=False)


    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['password', 'email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @staticmethod
    def search(question):
        queryset_by_name = CustomUser.objects.filter(username__icontains=question)
        queryset_by_email = CustomUser.objects.filter(email__icontains=question)

        queryset = (queryset_by_name | queryset_by_email).distinct()

        return queryset

    @property
    def get_image_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        else:
            return settings.MEDIA_ROOT + '/default_ava.png'

    @property
    def get_current_balance(self):
        return self.money_balance

    @property
    def is_user_blocked(self):
        return self.is_blocked

    @property
    def is_user_confirmed(self):
        return self.is_confirmed

    @property
    def is_user_staff(self):
        return self.is_staff

    class Meta:

        ordering = ['username']
        verbose_name = 'CustomUser'
        verbose_name_plural = 'CustomUsers'

class Subscriber(models.Model):
    objects = models.Manager()
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Subscriber'

class Profile(models.Model):

    objects = models.Manager()
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subs_by = models.ManyToManyField(Subscriber, related_name = 'subs')

    # def get_subs_count(self):
    #     profile = get_object_or_404(Profile, owner=self.owner)
    #     count = profile.subs_by.count()
    #
    #     return count

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

#Movie and related models:

class Genre(models.Model):
    objects = models.Manager()

    name = models.CharField(verbose_name='Genre name', max_length=100, null=False, blank=False, unique=True)
    description = models.TextField(verbose_name='Description', max_length=500, null=False, blank=False)
    url = models.SlugField(verbose_name='genre url', unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def search(question):
        queryset_movies = Movie.objects.filter(genre__name=question)
        return queryset_movies.distinct()

    class Meta:
        verbose_name = 'Genre'

class Movie(models.Model):
    objects = models.Manager()

    years = [(i, i) for i in range(2000, 2030)]

    countries = [('Russia', 'Russia'), ('USA', 'USA'), ('Germany', 'Germany'),
                 ('Britain', 'Britain'), ('France', 'France'), ('Italy', 'Italy'), ('Spain', 'Spain'),
                 ('Canada', 'Canada'), ('Mexico', 'Mexico'), ('China', 'China'), ('Japan', 'Japan'), ('South Korea', 'South Korea'),
                 ('Ukraine', 'Ukraine'), ('Norway', 'Norway'), ('Finland', 'Finland')]

    title = models.CharField(verbose_name='Movie name', unique=True, null=False,
            blank=False,
            max_length = 100)

    movie_logo = models.ImageField(verbose_name='Image Logo', default=settings.MEDIA_ROOT + '/default_movie_pic.jpg', blank=True, null=True)

    movie_video = models.FileField(verbose_name='Movie Video File', upload_to=settings.MEDIA_ROOT + '/videos',
    default=settings.MEDIA_ROOT + '/default_movie_video.gif', null=True, blank=True)

    description = models.TextField(verbose_name='Description', max_length=500, null=True, blank=True)

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    country = models.CharField(verbose_name='Country', choices=countries, default=countries[0][0], null=False, blank=False, max_length=40)

    year = models.PositiveSmallIntegerField(verbose_name='Date of announce', choices=years, default=2020)

    price = models.PositiveIntegerField(verbose_name='price', null=False, blank=False, default=100)

    liked_by = models.ManyToManyField(CustomUser, related_name='liked_posts')

    def __str__(self):
        return self.title

    @staticmethod
    def search(question):
        queryset = Movie.objects.filter(title__icontains=question)

        return queryset

    @property
    def get_movie_logo_url(self):
        if self.movie_logo and hasattr(self.movie_logo, 'url'):
            return self.movie_logo.url
        else:
            return settings.MEDIA_ROOT + '/default_movie_pic.jpg'

    @property
    def get_current_price(self):
        return self.price

    @property
    def get_movie_video_url(self):
        if self.movie_video and hasattr(self.movie_video, 'url'):
            return self.movie_video.url

        else:
            return settings.MEDIA_ROOT + '/default_movie_video.gif'

    def get_count_reviews(self):
        movie = get_object_or_404(Movie, title=self.title)
        count = movie.review_set.count()

        return count

    def get_count_likes(self):
        movie = get_object_or_404(Movie, title=self.title)
        count = movie.liked_by.count()

        return count

    @staticmethod
    def set_default_video():
        """Method sets default file instead of yours if it does not match require ones"""
        movie_video = settings.MEDIA_ROOT + '/default_movie_video.gif'

        return movie_video

    class Meta:
        ordering = ['-year', 'title']
        verbose_name_plural = 'Movies'

class Review(models.Model):
    objects = models.Manager()
    stars = [(star, star) for star in range(1, 6)]

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    author = models.ForeignKey(CustomUser, on_delete=models.PROTECT, default=None)
    text = models.TextField(verbose_name='Some Text', null=False, blank=False)
    star = models.PositiveSmallIntegerField(verbose_name='rating star', choices = stars, null = True, default=1)

    def __str__(self):
        return 'Review'

    class Meta:
        verbose_name = 'Review'

class Notification(models.Model):
    objects = models.Manager()

    message = models.TextField(
        verbose_name='Notification text',
        default=None,
        null=True, blank=True
    )
    notific_time = models.DateTimeField(verbose_name='Time to delete', auto_now_add=True, null=True, blank=True)
    is_expired = models.BooleanField(verbose_name='Is Expired', default=False)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ['-id']



