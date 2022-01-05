import io

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, UserChangeForm, \
    PasswordResetForm
from django.contrib.auth.forms import forms
from .models import *
from django.core.validators import *

class CustomUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        del self.fields['password1']

    username = forms.CharField(label='Username', widget=forms.TextInput, min_length=4, max_length=40,  required=True)

    email = forms.EmailField(label='E-mail', widget=forms.EmailInput, validators=[EmailValidator], required=True)

    gender = forms.ChoiceField(label='Gender', choices=CustomUser.genders, required=True)

    youtube_account_link = forms.URLField(label='Youtube Account link', widget=forms.URLInput, required=False)

    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)

    date_of_birth = forms.DateField(label='Date of Birth', widget=forms.SelectDateWidget, required=False)

    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput, required=True)

    username.widget.attrs.update({'form-class': 'form-input'})
    email.widget.attrs.update({'form-class': 'form-input'})

    password.widget.attrs.update({'form-class': 'form-input'})
    password2.widget.attrs.update({'form-class': 'form-input'})

    date_of_birth.widget.attrs.update({'form-class': 'form-input'})

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        user = CustomUser.objects.filter(username=username)
        if user.count() > 0:
            raise ValidationError('username already exists')

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if CustomUser.objects.filter(email=email).count() > 0:
            raise ValidationError('This email is already in the system')

        return email

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if gender is None:
            raise ValidationError('select your gender please')

        return gender

    def clean_password2(self):
        password1 = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password1 is None:
            raise ValueError('empty password in validation')

        if password2 is None:
            raise ValueError('empty password2 in validation')

        if password1 != password2:
            raise ValidationError('Password does not matches')

        return password2

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'gender', 'password', 'date_of_birth')

class CustomUserLoginForm(AuthenticationForm, forms.ModelForm):

    username = forms.CharField(label='Username', widget=forms.TextInput, required=True)

    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)

    username.widget.attrs.update({'form-class': 'form-input'})
    password.widget.attrs.update({'form-class': 'form-input'})

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

class MovieCreateForm(forms.ModelForm):

    movie_logo = forms.ImageField(label='Image', widget=forms.FileInput, required=True)

    title = forms.CharField(label='Movie Title', widget=forms.TextInput, required=True)

    description = forms.CharField(label='Movie Description', widget=forms.Textarea, required=True)

    movie_video = forms.FileField(label='Movie file', widget=forms.FileInput, required=True)

    genre = forms.ModelChoiceField(label='Genre', queryset=Genre.objects.all(),  required=True)

    country = forms.ChoiceField(label='Country', choices=Movie.countries, required=True)

    year = forms.ChoiceField(label='Year of announce', choices=Movie.years, required=True)

    price = forms.IntegerField(label='Price', required=True)

    movie_logo.widget.attrs.update({'form-class': 'form-input'})
    title.widget.attrs.update({'form-class': 'form-input'})
    description.widget.attrs.update({'form-class': 'form-input'})


    price.widget.attrs.update({'form-class': 'form-input'})
    movie_video.widget.attrs.update({'form-class': 'form-input'})
    genre.widget.attrs.update({'form-class': 'form-input'})

    class Meta:
        model = Movie
        fields = ['movie_logo', 'title', 'description', 'movie_video', 'genre', 'country', 'year', 'price']

class ProfileUpdateForm(forms.ModelForm):

    avatar = forms.ImageField(label='Avatar', widget=forms.FileInput, required=False)

    username = forms.CharField(label='Username', widget=forms.TextInput, required=False)

    email = forms.EmailField(label='Email', widget=forms.EmailInput, required=False)

    gender = forms.ChoiceField(label='Gender', choices=CustomUser.genders, required=False)

    avatar.widget.attrs.update({'form-class': 'form-input'})
    username.widget.attrs.update({'form-class': 'form-input'})

    email.widget.attrs.update({'form-class': 'form-input'})

    class Meta:
        model = CustomUser
        fields = ['avatar', 'username', 'email', 'gender']

    def clean_avatar(self):
        if self.cleaned_data['avatar'] and hasattr(self.cleaned_data['avatar'], 'url'):
            return self.cleaned_data['avatar']

    def clean_username(self):
        return self.cleaned_data['username']

    def clean_email(self):
        return self.cleaned_data['email']

    def clean_gender(self):
        return self.cleaned_data['gender']

class CreateReviewForm(forms.ModelForm):
    text = forms.CharField(label='Enter text:', widget=forms.TextInput, required=True)
    star = forms.ChoiceField(label='Rate', choices=Review.stars, required=True)

    star.widget.attrs.update({'form-class': 'form-input'})
    text.widget.attrs.update({'form-class': 'form-input'})
    class Meta:
        model = Review
        fields = ['text', 'star']

#
# class ShareMovieForm(forms.Form):
#     link = forms.URLField(label='URL', widget=forms.URLInput, required=False)

class SupportForm(forms.Form):
    message = forms.CharField(label='Enter Message', widget=forms.TextInput, required=True)

    message.widget.attrs.update({'form-class': 'form-input'})


class ResetForm(forms.ModelForm):
    username = forms.CharField(label='Current Username', widget=forms.TextInput, required=True)
    password = forms.CharField(label='New Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput, required=True)

    username.widget.attrs.update({'form-class': 'form-input'})
    password.widget.attrs.update({'form-class': 'form-input'})
    password2.widget.attrs.update({'form-class': 'form-input'})

    def clean_username(self):
        if self.cleaned_data.get('username') is not None:
            return self.cleaned_data['username']

        else:
            raise ValidationError('username is empty')

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        confirm = self.cleaned_data.get('password2')

        if password and confirm and password == confirm:
            return confirm

        else:
            raise ValidationError('passwords should be the same')

    class Meta:
        model = CustomUser
        fields = ['password']

class EmailInputForm(forms.Form):
    email = forms.EmailField(label='Enter Email', widget=forms.EmailInput, required=True)



