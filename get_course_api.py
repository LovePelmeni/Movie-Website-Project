import requests
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404, redirect

from .models import Movie
from .services import logger, valid_request_codes


def get_current_dollar_eq():
    """Parsing data from website about dollar course"""
    url = 'https://mainfin.ru/currency/usd/moskva'

    page = requests.get(url, timeout=10)
    filtered_tags = []
    if page.status_code in valid_request_codes:
        soup = BeautifulSoup(page.text, 'html.parser')

        tags = soup.find_all('td', class_='mark-text')
        for tag in tags:
            filtered_tags.append(tag.text)

        return {'course': round(float(filtered_tags[0]))}
    else:
        print('Could not connect, status: %s' % page.status_code)
        return None

def convert_price_to_dollars(request, **kwargs):
    """This method converting movie price to dollars, using dollar course parsed with get_current_dollar_eq()"""
    movie = get_object_or_404(Movie, title__iexact=kwargs.get('movie_title'))
    response = get_current_dollar_eq()
    #Trying to get a course and apply new kwargs pair to current session
    try:
        course = response.get('course')
        price = movie.price / course
        request.session['dollar_price'] = round(price, 1)

        return redirect(request.META.get('HTTP_REFERER')) #returns redirect to the same page

    except():
        logger.error('Problem with (dollar course)')
        return None

def convert_back(request):
    """This method converts back price to rubles"""
    course = request.session.get('dollar_price')
    if course is not None:
        request.session.pop('dollar_price')

        return redirect(request.META['HTTP_REFERER'])

