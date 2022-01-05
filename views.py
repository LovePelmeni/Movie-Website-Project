from django.db.models import Count
from django.shortcuts import render
# Create your views here.
from django.views import View
from django.views.generic import ListView

from . import services
from .forms import *
from .models import *
from .services import *

class MainPage(GeneralContextMixin, View):
    template_name = 'movie/index.html'
    allow_empty = True

    def get(self, request, **kwargs):
        context = self.get_context(request, **kwargs)
        context['title'] = 'Movie Website Project'
        # validated_movies = validate_movies()
        context.update({'queryset': Movie.objects.all(), 'banner': 'Main Page'})

        return render(request, self.template_name, context=context)

class GetGenreMovies(GeneralContextMixin, View):
    template_name = 'movie/genre.html'
    title = 'Genre Movies'

    def get(self, request, **kwargs):
        context = {}
        c_def = self.get_context(request, **kwargs)

        context.update({'title': self.title})
        context['banner'] = 'Genre Movies'
        genre_name = kwargs.get('genre_name')
        if genre_name is not None:
            queryset = Movie.objects.filter(genre__name=genre_name)
            context['queryset'] = queryset

        main = {**context, **c_def}

        return render(request, self.template_name, context=main)

class GetSingleMovie(GeneralContextMixin, View):
    template_name = 'movie/movie.html'
    context = {'banner': 'Movie'}

    def get(self, request, **kwargs):
        c_def = self.get_context(request, **kwargs)

        genre_name = kwargs.get('genre_name')
        if genre_name is not None:
            queryset = Movie.objects.filter(genre__name=genre_name)
            if queryset is not None:
                movie = get_object_or_404(Movie, title=kwargs.get('movie_title'))
                self.context['title'] = '%s Movie' % movie.title

                self.context.update({'movie': movie, 'dollar_price': request.session.get('dollar_price')})

        main = {**self.context, **c_def}

        return render(request, self.template_name, context=main)

class PostMovie(services.BaseViewClass):

    def __init__(self, template_name=None, context=None):
        super().__init__(template_name, context)

        self.template_name = 'movie/create_movie.html'
        self.context = {'banner': 'Add Movie', 'form': MovieCreateForm()}

    def get(self, request, **kwargs):
        return self.process_get(request, **kwargs)

    def post(self, request):
        new_movie = create_movie(request)
        if new_movie['status']:
            return HttpResponseRedirect(reverse('movie:home'))

        else:
            return render(request, 'movie/error.html', context={'error': 'Could not create movie'})

# #user view authentication classes:
class UserCreateView(services.BaseViewClass):

    def __init__(self, template_name=None, context=None):
        super().__init__(template_name, context)

        self.template_name = 'movie/registration.html'
        self.context = {'form': CustomUserForm(), 'title': 'Registration Page', 'banner': 'Registration'}
        self.error_context = {}

    def post(self, request):
        service = registration_service(request)
        if 'form_errors' in service:
            self.error_context.update({'error': service.get('form_errors')})

            return render(request, 'movie/error.html', context=self.error_context)

        else:
            print('User has been signed up successfully')
            return HttpResponseRedirect(reverse('movie:home'))

    def get(self, request, **kwargs):
        return self.process_get(request, **kwargs)

class UserLoginView(services.BaseViewClass):
    def __init__(self, template_name=None, context=None):
        super().__init__(template_name, context)

        self.template_name = 'movie/login.html'
        self.context = {'form': CustomUserLoginForm(), 'title': 'Login Page', 'banner': 'Login'}

        self.error_context = {}

    def post(self, request):
        service = user_login_service(request)
        if service['status']:
            return HttpResponseRedirect(reverse('movie:home'))
        else:
            return render(request, 'movie/error.html', context={'error': 'Could not login, wrong password or login'})

    def get(self, request, **kwargs):
        return self.process_get(request, **kwargs)

class GetUserProfileView(services.BaseViewClass):

    def __init__(self, template_name=None, context=None):
        super().__init__(template_name, context)
        self.template_name = 'movie/profile.html'
        self.context = {'banner': 'Profile', 'title': 'User Profile'}

    def get(self, request, **kwargs):
        self.context.update({**get_user_profile(request, **kwargs)})
        # if service:
        #     self.context.update({'profile': service['profile']})
        return self.process_get(request, **kwargs)

class EditUserProfileView(GeneralContextMixin, View):
    template_name = 'movie/edit_profile.html'
    context = {}
    context['banner'] = 'Edit'
    context['title'] = 'Edit Profile'

    def get(self, request, **kwargs):
        c_def = self.get_context(request, **kwargs)
        initial_profile_data = {'avatar': request.user.avatar, 'username': request.user.username, 'email': request.user.email,
        'gender': request.user.gender}

        self.context['form'] = ProfileUpdateForm(initial=initial_profile_data)

        main = {**c_def, **self.context}

        return render(request, self.template_name, context=main)

    def post(self, request):
        service = edit_user_profile(request)
        context = {}
        if service['status']:
            context['username'] = service.get('user').username
            context['banner'] = service.get('message')
            return render(request, 'movie/edit_done.html', context=context)

        else:
            return render(request, 'movie/error.html', context={'errors': service['errors'],
            'message': 'Could not update your profile :('})

class SendConfirmByEmail(GeneralContextMixin, View):
    template_name = 'movie/done.html'
    context = {}
    context['time'] = timezone.now()

    def get(self, request, **kwargs):
        username = kwargs.get('username')
        service_send_confirm = send_confirm_profile_service(request, username=username)
        if service_send_confirm:
            return render(request, self.template_name, context={'banner': 'We sended confirm link on your email!'})
        else:
            return render(request, 'movie/error.html', context={'message': 'Failed to send confirm'})

class CheckConfirmByEmail(GeneralContextMixin, View):

    def get(self, request, **kwargs):
        username = kwargs.get('uid64')

        service_check_confirm = check_profile_confirm_service(request, uid64=username)
        if service_check_confirm:
            return HttpResponseRedirect(reverse('movie:get_profile', kwargs={'username': service_check_confirm}))

class WebSearch(GeneralContextMixin, View):
    template_name = 'movie/searcher.html'

    def get(self, request, **kwargs):
        search_for = WebSearch_service(request)
        context = self.get_context(request, **kwargs)
        if search_for.items() is None:
            context.update({'message': 'There is no such objects:( '})

        return render(request, self.template_name, {**context, **search_for})

class Review(GeneralContextMixin, View):
    template_name = 'movie/reviews.html'
    context = {}

    def get(self, request, **kwargs):
        upper_context = self.get_context(request, **kwargs)
        reviews = get_all_reviews(request, movie_title=kwargs.get('movie_title'))

        self.context = {**upper_context, **reviews}
        self.context['form'] = CreateReviewForm()

        return render(request, self.template_name, context=self.context)

    def post(self, request, **kwargs):

        if request.user.is_authenticated:
            post_review = create_review(request, **kwargs)
            if post_review['status']:
                return HttpResponseRedirect(reverse('movie:home'))
            else:
                return render(request, 'movie/error.html', context={
                    'error': 'Could not add review'
                }
    )

class Support(services.BaseViewClass):
    def __init__(self, template_name=None, context=None):
        super().__init__(template_name, context)

        self.template_name = 'movie/support.html'
        self.context = {'form': SupportForm(), 'banner': 'Support Page'}

    def get(self, request, **kwargs):
        return self.process_get(request, **kwargs)

    def post(self, request, **kwargs):
        return services.send_support_message(request, form=SupportForm, **kwargs)

class WatchMovie(GeneralContextMixin, View):
    template_name = 'movie/watch.html'

    def get(self, request, **kwargs):
        watch_movie = get_movie_file(request, **kwargs)
        upper_context = self.get_context(request, **kwargs)

        main = {**watch_movie, **upper_context}

        return render(request, self.template_name, context=main)

class GetEmailEnterPage(GeneralContextMixin, View):
    template_name = 'movie/enter_email.html'

    def get(self, request, **kwargs):
        context = {
            'form': EmailInputForm()
        }
        upper_context = self.get_context(request, **kwargs)

        return render(request, self.template_name, context={**context, **upper_context})

    def post(self, request, **kwargs):
        service_send = send_reset_password_message(request)
        if service_send:
            return render(request, 'movie/done.html', context={'banner': 'We sended reset message on your email'})



