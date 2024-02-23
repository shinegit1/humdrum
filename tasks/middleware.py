from django.http import Http404
from django.shortcuts import render


class ErrorPageFallbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code >= 400:
            try:
                return render(request, 'tasks/http_error.html', status=response.status_code)
            except Http404:
                pass

        return response
