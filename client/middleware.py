from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class MyExceptionMiddleWare(MiddlewareMixin):
    def process_exception(self,request,exception):
        if settings.DEBUG == False:
            pass
        res = {
            "code":10,
            "msg":str(exception),
            "data":""
        }

        return JsonResponse(res)
