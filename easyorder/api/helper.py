from rest_framework.response import Response
from rest_framework import status


class ApiResponse():
    def __init__(self, data={}, status=status.HTTP_201_CREATED, headers=None):
        self.data = data
        self.status = status
        self.headers = headers

    def response(self):
        return Response(data=self.data, status=self.status, headers=self.headers)
