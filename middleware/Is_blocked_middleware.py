import datetime
import time
from django.contrib.auth import logout
from django.http import HttpResponseForbidden
from django.shortcuts import render
from datetime import datetime
from .models import CustomUser

from django.core.exceptions import *
from django.utils.deprecation import *

class IsBlockedMiddleware(MiddlewareMixin):

    def __call__(self, request):
        response = self.get_response(request)

        return response

    def process_view(self, request):

        if request.user.is_authenticated:
            user = CustomUser.objects.get(username=request.user.username)
            if user.is_blocked:
                time_format = time.time()
                current_processed_time = datetime.date.fromtimestamp(time_format)
                block_time = current_processed_time.day - datetime.timedelta(days=1).days
                current_time = datetime.now().day

                if current_time < block_time:
                    user.is_blocked = False
                    return None

                else:
                    raise PermissionDenied(f'You are blocked on this website {datetime.now().day + 1} of current month')

            else:
                return None

            
