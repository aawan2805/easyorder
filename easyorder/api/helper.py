import json
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse


class ApiResponse(): 
    def __init__(self, data={}, status=status.HTTP_201_CREATED, headers={}):
        self.response = Response(data, status=status, headers=headers)

    def get_response(self):
        return self.response
