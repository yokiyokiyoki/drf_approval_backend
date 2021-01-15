from django.http import JsonResponse, HttpResponse


import json

import logging


class ResponseMiddleware:
    def __init__(self, get_response):
        print("程序启动时执行, 只执行一次")
        self.get_response = get_response

    def __call__(self, request):
        print("中间件开始")
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        print("process_view")

    def process_exception(self, request, exception):
        print("程序异常时执行", exception)

        logging.exception(exception)
        return JsonResponse({"message": exception.args[0], "status": -1})
