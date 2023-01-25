from api.views import CategoryView
from django.urls import get_resolver

API_URL = "api"

class BrandCookieMiddleware:
    allows_url_path = '/api'
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.split("/")[1] == API_URL:
            print("API URL")
            # Check the status of the order?
            # Check the cookie status if order is not done yet.
            # Set cookie if cookie is expired.
