from api.views import CategoryView
from django.urls import get_resolver
from panel.models import Order

API_URL = "api"
ROOT_URL = "/"
ALLOWED_URLS = [
    "/api/category/",
    "/api/dishes/",
    "/api/order"
]

class BrandCookieMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        # Code to be executed for each request/response after
        if request.path != ROOT_URL and any([request.path.startswith(url) for url in ALLOWED_URLS]):
            if 'collection_code' in request.COOKIES:
                print("Set", request.COOKIES['collection_code'])
            else:
                print("NOT SET")
        response['Access-Control-Allow-Credentials'] = 'true'
        return response


        # Check the status of the order?
        # Check the cookie status if order is not done yet.
        # Set cookie if cookie is expired.
