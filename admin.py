from django.contrib import admin
from .models import *
# Register your models here.

class CustomUserInline(admin.StackedInline):
    model = CustomUser
    can_delete = True
    verbose_name_plural = 'CustomUsers'

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    verbose_name_plural = 'Profiles'

class MovieInline(admin.StackedInline):
    model = Movie
    can_delete = True
    verbose_name_plural = 'Movies'

class GenreInline(admin.StackedInline):
    model = Genre
    can_delete = True
    verbose_name_plural = 'Genres'

class ReviewInline(admin.StackedInline):
    model = Review
    can_delete = True
    verbose_name_plural = 'Reviews'

class NotificationInline(admin.StackedInline):
    model = Notification
    can_delete = True
    verbose_name_plural = 'Notifications'

class CustomUserAdmin(admin.ModelAdmin):
    fields = ['username', 'gender', 'ip_address', 'password',
    'email', 'avatar', 'money_balance', 'date_of_birth',
    'last_online', 'is_staff', 'is_blocked', 'is_confirmed', 'is_superuser']

    list_filter = ['username', 'email']

    list_display = ('username', 'gender', 'ip_address', 'password', 'email', 'avatar', 'date_of_birth',
    'last_online', 'is_staff', 'is_blocked', 'is_confirmed', 'is_superuser')

    @admin.display(description='username')
    def upper_case_name(self, obj):
        return ('%s %s' % obj.username).upper()


admin.site.register(CustomUser, CustomUserAdmin)


class ProfileAdmin(admin.ModelAdmin):
    fields = ['owner', ]
    list_display = ('owner',)

    @admin.display(description='owner')
    def upper_case_name(self, obj):
        return ('%s %s' % obj.owner.username).upper()


admin.site.register(Profile, ProfileAdmin)

class MovieAdmin(admin.ModelAdmin):
    fields = ['title',  'movie_logo', 'description', 'movie_video', 'genre', 'country', 'year', 'price']
    list_display = ('title', 'movie_logo', 'description', 'movie_video', 'genre', 'country', 'year', 'price')

    @admin.display(description='title')
    def upper_case_name(self, obj):
        return ('%s %s' % obj.title).upper()

admin.site.register(Movie, MovieAdmin)

class GenreAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'url']
    list_display = ('name', 'description', 'url')

    @admin.display(description='name')
    def upper_case_name(self, obj):
        return ('%s %s' % obj.name).upper()

admin.site.register(Genre, GenreAdmin)

class ReviewAdmin(admin.ModelAdmin):
    fields = ['text']
    list_display = ('text',)

    @admin.display(description='text')
    def upper_case_name(self, obj):
        return ('%s %s' % obj.text).upper()

admin.site.register(Review, ReviewAdmin)


class NotificationAdmin(admin.ModelAdmin):
    fields = ['message', 'notific_time']
    list_display = ('message', 'notific_time')

    @admin.display(description='message')
    def upper_case_name(self, obj):
        return ('%s %s' % obj.message).upper()

admin.site.register(Notification, NotificationAdmin)

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['user']
    fields = ['user']

admin.site.register(Subscriber, SubscriberAdmin)






