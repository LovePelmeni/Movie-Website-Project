import os

import requests
from bs4 import BeautifulSoup
from django.core import exceptions
from django.db.models import F, Max, Min, When, ExpressionWrapper, Count
from django.db.models.functions import Cast
from django.template import Context
from django.template.context_processors import csrf
from django.views import View
from django.views.generic.edit import FormView
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.validators import validate_email
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseNotFound, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.dispatch import Signal
from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status

from .delete_all_user_data import delete_all_user_data
from .forms import CustomUserForm, ProfileUpdateForm, CreateReviewForm, MovieCreateForm, ResetForm, \
    EmailInputForm

from .models import *
import logging

sign_up_done = dispatch.Signal()
updated_profile = dispatch.Signal()

valid_request_codes = [code for code in range(200, 211)]

logger = logging.getLogger(__name__)

class GeneralContextMixin(object):
    """This is base context Mixin for all view classes"""
    query_of_notifications = Notification.objects.exclude(is_expired=False)
    query_of_genres = Genre.objects.all()

    def get_context(self, request, **kwargs) -> dict:
        """This method returns a main context for page"""
        context = kwargs
        context.update({'notifications': self.query_of_notifications})
        context['genres'] = self.query_of_genres

        return context

class BaseViewClass(GeneralContextMixin, View):
    """This is an extension class for CBV to simplify code"""
    def __init__(self, template_name, context):
        super().__init__()

        self.template_name = template_name
        self.context = context

    def process_get(self, request, **kwargs):
        bar_context = self.get_context(request, **kwargs)
        bar_context.update(csrf(request))

        main = {**self.context, **bar_context}

        return render(request, self.template_name, main)

def send_mail(request, title, email_body, user_email):
    """This method sending email"""
    email = EmailMessage(
        title,
        email_body,
        os.getenv('EMAIL_HOST_USER'),
        [user_email]
    )
    email.send(fail_silently=False)

    return HttpResponse(True, status=202)

def send_confirm_profile_service(request, username):
    """This method sending email message on your email to confirm your profile in system"""

    if CustomUser.objects.filter(username__iexact=username).exists():
        user = get_object_or_404(CustomUser, username=username)
        encoded_username = urlsafe_base64_encode(smart_bytes(user.username))
        #Getting domain of our website ... and forming url for link with encoded username
        domain = get_current_site(request=request).domain
        url = reverse('movie:check-email', kwargs={'uid64': encoded_username})
        #Creating full url...
        absolute_url = 'http://' + domain + url
        #Creating email body (message) which gonna be sended out to user for confirmation...
        email_body = f'Hello, {user.username}! \n This is your link to confirm your profile. \n' \
        f'Follow: {absolute_url} \n' \
        f'Main Dev. Kirill \n' \
        f'{timezone.now().strftime("%D, %H:%M")}'

        #sending email to user...
        send_mail(request, title='Confirm Email', email_body=email_body, user_email=user.email)
        #If Alright, returns an HttpResponse with status code 200...
        return HttpResponse(status=status.HTTP_202_ACCEPTED)
    else:
        return False

def check_profile_confirm_service(request, uid64):
    """This method checks for existence of user and sets that user is confirmed"""
    list_usernames = CustomUser.objects.values_list('username', flat=True)

    decoded_username = smart_str(urlsafe_base64_decode(uid64))
    if decoded_username in list_usernames:
        user = get_object_or_404(CustomUser, username=decoded_username)
        #Checking for user confirmed status
        if not user.is_confirmed:
            user.is_confirmed = True
            logger.debug('User Confirmed')

            user.save()
            #returns dict with decoded username....
        return decoded_username

    else:
        raise Http404('There is no such user')

def registration_service(request):
    """This method is used for signing up users to the system"""
    form_class = CustomUserForm
    #model
    user = auth.get_user(request)
    #Function parameters up there:
    if user.is_authenticated:
        return HttpResponseRedirect(reverse('movie:login'))

    user_form = form_class(request.POST or None)
    #Checking for form validation:
    if user_form.is_valid():
        new_user = CustomUser.objects.create_user(username=user_form.cleaned_data.get('username'), email=user_form.cleaned_data['email'],
        password=user_form.cleaned_data['password2'])
            #Printing user was created to make sure it works....

        login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')
        logger.info('User was authenticated')
            #sending signal out..
        try:
            sign_up_done.send(sender=registration_service, created=True, instance=new_user)
            logger.debug('notification sent')
        except():
                pass

        return HttpResponse(True, status=status.HTTP_200_OK)

    else:
        return {'form_errors': user_form.errors}

def user_login_service(request):
    """This is base login method that helps to sign in user to the Database"""

    username = request.POST.get('username')
    password = request.POST.get('password')

    try:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            logger.debug('User was signed in successfully')# All this prints just to make sure the system works:)
            return {'status': True}
                #Else BUNCH of different exceptions...
    except():
        return {'status': False}

@login_required
def get_user_profile(request, **kwargs):
    """Method, that returns a user profile"""
    user = get_object_or_404(CustomUser, username=kwargs.get('username'))
    if user is not None:
        return {'profile': get_object_or_404(Profile, owner=user), 'user': user}

    else:
        raise Http404('There is no such profile')

@login_required
def logout_user(request):
    """Method to log out user from system"""
    logout(request)
    logger.debug('user is logout')

    return redirect('/')

def get_class_name(value):
    return value.__name__

#Warning:
#If adding new model to sort, create a search method in the model, that's important
def WebSearch_service(request):
    """Searcher from db, use to find some objects"""
    context = {}

    list_of_models = [
        CustomUser,
        Movie,
        Genre
    ]

    question = request.GET.get('question')
    #Parameters up there...
    if question is not None:
        for model_elem in list_of_models:
            filter = model_elem.search(question=question)
            context[get_class_name(model_elem)] = filter
            #Forming current_page context for different content
    #Returns context...
    return context

def update_user(user, **kwargs):
    """Method checks that fields is filled up and updating user"""
    for key, elem in kwargs.items():
        setattr(user, key, elem)

    user.save()
    return user

@login_required
def edit_user_profile(request):
    """This method edit user profile (CustomUser data)"""
    form_class = ProfileUpdateForm
    data_to_change = {}
    user = get_object_or_404(CustomUser, username__iexact=auth.get_user(request).username)
    context = {}

    if request.POST.items() is not None:
        update_form = form_class(request.POST, request.FILES, initial={'avatar': user.avatar,
        'username': user.username, 'email': user.email, 'gender': user.gender})

        if update_form.has_changed():

            for field in update_form.changed_data:

                if field in request.FILES:
                    data_to_change[field] = request.FILES[field]

                else:
                    data_to_change[field] = request.POST[field]

            update_user(user=user, **data_to_change)
            updated_profile.send(sender=edit_user_profile, request=request, instance=user, updated=True)

            context.update({'status': True, 'user': user, 'message': 'Congratulations!'})
        else:
            context.update({'status': False, 'errors': update_form.errors})

    return context

@login_required
def delete_account(request, **kwargs):
    """This method used to delete your account"""
    user = CustomUser.objects.get(username=kwargs.get('username'))
    if user is not None:
        logout(request)
        delete_all_user_data(username=user.username)
        logger.info('User has been deleted')

        return HttpResponseRedirect(reverse('movie:home'))

def check_movie_video_format(movie_video) -> bool:
    """This function checks for available video formats. I use it in form validation (forms.py)"""
    file_name = movie_video.name
    list_of_formats = ['.mp4', '.ogv', '.mov', '.mpeg', '.webm', '.gif']

    filename, extension = os.path.splitext(file_name)

    if extension.lower() not in list_of_formats:
        logger.debug('Format does not matches( ')
        return False

    else:
        logger.debug('Format matches ')
        return True

def get_default_video():
    """Method sets default file instead of yours if it does not match require ones"""
    movie_video = settings.MEDIA_ROOT + '/default_movie_video.gif'

    return movie_video

def create_movie(request):
    """This method creates movie"""
    model = Movie
    if not auth.get_user(request).is_authenticated:
        return HttpResponseRedirect(reverse('movie:registration'))

    movie_form = MovieCreateForm(request.POST, request.FILES)
    if movie_form.is_valid():
        file = request.FILES.get('movie_video')
        new_movie = model.objects.create(**movie_form.cleaned_data)
        #if checks returns False, then sets default video
        new_movie.save()
        #Checking for available of video format
        check_valid_ext = check_movie_video_format(movie_video=file)

        if not check_valid_ext:
            new_movie.movie_video = get_default_video()
            new_movie.save()

        return {'status': True, 'status_code': status.HTTP_201_CREATED}

    else:
        return {'status': False, 'status_code': status.HTTP_400_BAD_REQUEST}

@login_required
def create_review(request, movie_title=None):
    """This method creates review for movie"""
    form_class = CreateReviewForm
    movie = Movie.objects.get(title=movie_title)
    author = get_object_or_404(CustomUser, username__iexact=auth.get_user(request).username)
    if movie is not None:
        review_form = form_class(request.POST or None)

        if review_form.is_valid():
            Review.objects.create(movie=movie, author=author, **review_form.cleaned_data)

            return {'status': True, 'status_code': status.HTTP_201_CREATED}
    else:
        return {'status': False}

def delete_review(request, **kwargs):
    """This method helps you to delete review"""
    review = Review.objects.get(id=kwargs.get('review_id'))

    review.delete()
    logger.debug('review was deleted')

    return redirect('movie:home')

def get_all_reviews(request, movie_title=None):
    """This method returns a queryset of related reviews for movie"""
    context = {}
    movie = get_object_or_404(Movie, title=movie_title)
    all_reviews = movie.review_set.all().order_by(
        '-author'
    )
    context.update({"current_movie": movie, 'all_reviews': all_reviews})

    return context

@login_required
def create_review(request, movie_title=None):
    """This method creates review for movie"""
    form_class = CreateReviewForm
    movie = Movie.objects.get(title=movie_title)
    author = get_object_or_404(CustomUser, username__iexact=auth.get_user(request).username)
    if movie is not None:
        review_form = form_class(request.POST or None)

        if review_form.is_valid():
            Review.objects.create(movie=movie, author=author, **review_form.cleaned_data)

            return {'status': True, 'status_code': status.HTTP_201_CREATED}
    else:
        return {'status': False}

@login_required
def send_support_message(request, form):
    """This method used to sending support messages directly to email address"""
    message_form = form(request.POST)

    if message_form.is_valid():
        full_message = 'User: %s \n %s time: %s' % (request.user.username, message_form.cleaned_data.get('message'),
        timezone.now().strftime('%d, %H:%M'))

        send_mail(request, title='New Support Message', email_body=full_message, user_email=settings.SUPPORT_EMAIL)

        return render(request, 'movie/done.html', context={'banner': 'We sended this message to support email'})

def get_movie_file(request, **kwargs):
    """This method returns movie file video"""
    title = kwargs.get('movie_title')

    if Movie.objects.filter(title=title) is not None:
        movie = get_object_or_404(Movie, title=title)
        movie_file = movie.movie_video

        return {'movie': movie_file, 'banner': movie.title}

def send_reset_password_message(request):
    """This method sending message with password reset instructions"""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('movie:home'))

    email = request.POST.get('email')

    if CustomUser.objects.filter(email=email) is not None:
        link = reverse('movie:password_reset')
        domain = get_current_site(request).domain

        full_url = 'http://' + domain + link
        message = 'Hello, \n This is your link to reset your password: %s' % full_url

        send_mail(request, title='Movie Project. Password Reset', email_body=message, user_email=email)

        return {'status': True}

    else:
        return {'status': False}

class ResetPasswordFormView(FormView):
    """This is reset CBV i use to reset password"""
    template_name = 'movie/reset.html'
    form_class = ResetForm

    def get_form_kwargs(self):
        context = super(ResetPasswordFormView, self).get_form_kwargs()
        return context

    def form_valid(self, form, **kwargs):
        user = get_object_or_404(CustomUser, username=form.cleaned_data['username'])
        new_password = form.cleaned_data.get('password2')
        user.password = new_password

        user.set_password(new_password)
        user.save()

        logger.info(f'password has been changed User:{user.username}')

        return HttpResponseRedirect(reverse('movie:login'))

    def form_invalid(self, form):
        logger.debug('form invalid in password reset')
        form.clean()
        return HttpResponseRedirect(reverse('movie:password_reset'))

def add_or_cancel_like(request, **kwargs):
    """This method adds likes to movie or removes it if you already done it before"""
    if not request.user.is_authenticated:
        return redirect('movie:login')

    user = get_object_or_404(CustomUser, username=request.user.username)
    movie = Movie.objects.get(title=kwargs.get('movie_title'))

    related_likes = movie.liked_by.all()

    if user not in related_likes:
        movie.liked_by.add(user)
        logger.debug(f'Like was added to movie: {movie.title}')

        return HttpResponseRedirect(reverse('movie:home'))
    else:
        #if user already liked movie, we cancel it
        movie.liked_by.remove(user)
        return HttpResponseRedirect(reverse('movie:home'))
