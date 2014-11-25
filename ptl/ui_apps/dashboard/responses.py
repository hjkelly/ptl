from django.http import HttpResponse


class JsonResponseCreated(HttpResponse):
    status_code = 201


class JsonResponseUnprocessable(HttpResponse):
    status_code = 422


class HttpResponseNoContent(HttpResponse):
    status_code = 204
