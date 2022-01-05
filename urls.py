from django.urls import path
from . import views, services, get_course_api
from .views import *

app_name = 'movie'

urlpatterns = [
    #get movie urls:
    path('', views.MainPage.as_view(), name='home'),
    path('movies/<str:genre_name>/', views.GetGenreMovies.as_view(), name='genres'),
    path('movies/<str:genre_name>/<str:movie_title>/', views.GetSingleMovie.as_view(), name='single_movie'),
    path('create_movie/', views.PostMovie.as_view(), name='create_movie'),

    # Conversion urls:
    path('convert/to/dollars/price/<str:movie_title>/', get_course_api.convert_price_to_dollars, name='to_dollars'),
    path('convert/back/', get_course_api.convert_back, name='convert_back'),

    # like/dislike urls:
    path('like/movie/<str:movie_title>/', services.add_or_cancel_like, name='like_or_cancel'),

    # watch url:
    path('watch/movie/<str:movie_title>/', views.WatchMovie.as_view(), name='watch'),

    # reviews urls:
    path('reviews/<str:movie_title>/', views.Review.as_view(), name='get_reviews'),
    path('delete/review/<int:review_id>/', services.delete_review, name='delete_review'),

    # #user urls:
    path('register/', views.UserCreateView.as_view(), name='registration'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', services.logout_user, name='logout'),

    #reset_password urls:
    path('enter/email/reset/', views.GetEmailEnterPage.as_view(), name='enter_email'),
    path('password/reset/', services.ResetPasswordFormView.as_view(), name='password_reset'),

    #user profile urls:
    path('get-user-profile/<str:username>/', views.GetUserProfileView.as_view(), name='get_profile'),
    path('edit-user-profile/', views.EditUserProfileView.as_view(), name='edit_profile'),
    path('delete/profile/<str:username>/', services.delete_account, name='delete_profile'),

    # #email checks urls:
    path('send-email-confirm/<str:username>/', views.SendConfirmByEmail.as_view(), name='send-email'),
    path('check-email-confirm/<uid64>/', views.CheckConfirmByEmail.as_view(), name='check-email'),

    #searcher url:
    path('searcher/', views.WebSearch.as_view(), name='search'),

    #support url:
    path('support/', views.Support.as_view(), name='support'),

]





