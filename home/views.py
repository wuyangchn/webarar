from django.http import JsonResponse
from django.shortcuts import render
import json
from . import models
from programs import http_funcs, log_funcs, ap, version


# Create your views here.
def show(request):
    if http_funcs.is_ajax(request):
        # 写数据表
        fingerprint = json.loads(request.body.decode('utf-8'))['fingerprint']
        http_funcs.set_user_sql(request, models.User, fingerprint)
        return JsonResponse({})
    else:
        log_funcs.write_log(http_funcs.get_ip(request), 'info', 'Visit home html')
        return render(request, 'home.html', {'ararpy_version': ap.version, 'web_version': version})




