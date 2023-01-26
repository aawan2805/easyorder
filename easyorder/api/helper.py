import json
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse


class ApiResponse():
    def __init__(self, data={}, status=status.HTTP_201_CREATED):
        self.response = HttpResponse(json.dumps(data), content_type="application/json")
        self.response.status_code = status

    def set_cookie(self, key, value, max_age=60*60):
        self.response.set_cookie(key, value, max_age=max_age)
        self.response['Access-Control-Allow-Credentials'] = 'true'

    def get_response(self):
        return self.response
