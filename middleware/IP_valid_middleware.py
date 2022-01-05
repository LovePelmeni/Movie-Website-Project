from django.http import HttpResponseForbidden


class ValidIPMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_ip_list = ['127.0.0.1']

    def __call__(self, request):
        response = self.get_response(request)

        return response

    def process_request(self, request):
        current_ip = request.META.get('REMOTE_ADDR')

        if current_ip not in self.allowed_ip_list:
            return HttpResponseForbidden('You have a forbidden IP ADDRESS')

        else:
            return None
