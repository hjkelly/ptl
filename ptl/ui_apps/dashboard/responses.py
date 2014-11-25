from django.http import HttpResponse, JsonResponse


class JsonResponseCreated(JsonResponse):
    status_code = 201


class JsonResponseUnprocessable(JsonResponse):
    status_code = 422


class HttpResponseNoContent(HttpResponse):
    status_code = 204
