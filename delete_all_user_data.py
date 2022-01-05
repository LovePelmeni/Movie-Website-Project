from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from .models import *

def delete_all_user_data(username):

    user = get_object_or_404(CustomUser, username=username)
    list_of_models = [

    CustomUser,
    Profile,
    Subscriber,
    Review,
    Movie
]
    for model in list_of_models:
        try:
            out_data = model.objects.get(model, **user)
        except MultipleObjectsReturned:
            out_data = model.objects.filter(**user)

        except ObjectDoesNotExist:
            continue

        out_data.delete()

        return None


