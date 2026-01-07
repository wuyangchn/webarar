from django.http import JsonResponse
from django.shortcuts import render
import json
from . import models
from programs import basic_funcs, http_funcs, log_funcs, ap, version


# Create your views here.
def show(request):
    user_id = request.COOKIES.get("anonymous_user_id")
    print(f"{user_id = }")
    if user_id:
        http_funcs.set_user_sql(request, models.User, user_id)
    if basic_funcs.is_ajax(request):
        # # 写数据表
        # user_id = request.COOKIES.get("anonymous_user_id")
        # http_funcs.set_user_sql(request, models.User, user_id)
        return JsonResponse({})
    else:
        # log_funcs.write_log(basic_funcs.get_ip(request), 'info', 'Visit home html')
        return render(request, 'home.html', {'ararpy_version': ap.version, 'web_version': version})




