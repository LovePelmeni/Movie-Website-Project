from django.http import HttpResponseForbidden
from django.core.exceptions import *
from django.utils.deprecation import *


class ValidIPMiddleware(MiddlewareMixin):

    allowed_ip_list = ['127.0.0.1']

    def __call__(self, request):
        response = self.get_response(request)

        return response

    def process_request(self, request):
        current_ip = request.META.get('REMOTE_ADDR')

        if current_ip not in self.allowed_ip_list:
            raise PermissionDenied('You are using invalid IP Address for this website')

        else:
            return None
