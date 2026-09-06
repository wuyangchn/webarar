import os
import pickle
import json
import traceback
from urllib.parse import urlparse, parse_qs
from django.http import JsonResponse, HttpResponse, FileResponse
from django.core.cache import cache
from django.core.exceptions import *
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import Http404
# from django.contrib.auth import logout
from calc import models
from . import ap, log_funcs
from .basic_funcs import get_ip, get_device, touch_cache, set_cache

DEFAULT_CACHE_TIMEOUT = 86400


def set_user_sql(request, mysql, user_id):
    if mysql.objects.filter(uuid=str(user_id)).exists():
        _user = mysql.objects.get(uuid=str(user_id))
        _user.count = _user.count + 1
        _user.ip = get_ip(request)
        _user.device = get_device(request)
        _user.save()
    else:
        mysql.objects.create(
            uuid=str(user_id),
            ip=get_ip(request),
            device=get_device(request),
            count=1
        )


def open_object_file(user_id, cache_key):
    cache_value = cache.get(f"user:{user_id}:data:{cache_key}:obj")
    if cache_value is None:
        raise Http404(f"Object not found. The cache might not exist or have been expired, key = {cache_key} ")
    sample = pickle.loads(cache_value)
    allIrraNames = list(models.IrraParams.objects.values_list('name', flat=True))
    allCalcNames = list(models.CalcParams.objects.values_list('name', flat=True))
    allSmpNames = list(models.SmpParams.objects.values_list('name', flat=True))
    return {'cache_key': json.dumps(cache_key), 'webFilePath': json.dumps(f"v={sample.version}, user={user_id}"),
            'allIrraNames': allIrraNames, 'allCalcNames': allCalcNames, 'allSmpNames': allSmpNames,
            'sampleComponents': ap.smp.json.dumps(ap.smp.basic.get_components(sample))}


def upload(file, media_dir, request=None, user_id=None, mysql=None, check_suffix=True):
    try:
        uid = ap.calc.basic.random_choice(length=8)
        name, suffix = os.path.splitext(file.name)
        if check_suffix and suffix.lower() not in [
            '.xls', '.age', '.xlsx', '.arr', '.jpg', '.png', '.txt',
            '.log', '.seq', '.json', '.ahd', '.csv', '.ngxdp']:
            raise TypeError(f"Unsupported file format: {suffix}")
        # web_file_path = os.path.join(media_dir, file.name)
        web_file_path = os.path.join(media_dir, f"{uid}{suffix}")
        with open(web_file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        # print("File path on the server: %s" % web_file_path)
    except PermissionError:
        raise ValueError(f'Permission denied')
    except (Exception, BaseException) as e:
        raise ValueError(f'Error in opening file: {e}')
    else:
        # write to database
        # name, file path on server, ip, device, ....
        if request:
            ip = get_ip(request)
            user_id = request.COOKIES.get("anonymous_user_id") if user_id is None else user_id
            mysql = models.ReceivedFiles if mysql is None else mysql
            if user_id:
                mysql.objects.create(
                    uuid=str(user_id),
                    ip=ip,
                    file_path=web_file_path,
                    original_name=file.name,
                    deleted=False,
                )
        return web_file_path, name, suffix


class AnonymousUserIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 处理请求
        response = self.get_response(request)
        # 匿名用户：检查是否有匿名ID Cookie
        anonymous_id = request.COOKIES.get("anonymous_user_id")

        # 已登录用户跳过（直接用user.id识别）
        # logout(request)
        # print(f"用户是否登录：{request.user.is_authenticated}")
        # print(f"用户对象：{type(request.user)}")

        if request.user.is_authenticated and anonymous_id:
            return response

        if not anonymous_id:
            # 生成唯一ID（UUID4随机且唯一）
            anonymous_id = ap.calc.basic.random_choice(length=8)

        # 设置Cookie（过期时间：365天，可调整）
        response.set_cookie(
            key="anonymous_user_id",
            value=anonymous_id,
            max_age=100 * 365 * 24 * 60 * 60,  # 100年有效期
            httponly=True,  # 禁止JS读取，防止XSS攻击
            secure=request.is_secure(),  # HTTPS下启用（生产环境推荐）
            samesite="Lax"  # 防止CSRF攻击
        )
        return response


class ArArView(View):
    """
    This class is rewritten based on View and is used to dispatch requests from client side.

    A request will first classified based on its method, including 'get', 'post' and others
    (see detail in class attribution http_method_names of View class); For each method, a
    function with the same name is required to handle it. Here I rewrite POST function,
    because I usually need to use <flag> to identify some special requests.

    In dispatch function, ajax requests are identified based on the flag value contained
    in request body.

    Some examples:
        1. POST request from a form, will go to <post> function, and then be dispatched
        according to the <flag> value, which is set as a hidden input;
        2. POST request from Ajax need to contain a <flag> value to let it identified. Two
        ways can be used, sending flag in url or body;
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize
        self.user_id = ''
        self.ip = ''
        self.device = ''
        self.flag = ''
        self.body = {}
        self.content = {}
        self.cache_key = ''
        self._cache_key = ''
        self.sample = ...
        self.fingerprint = ...
        self.handler = ...
        self.method = ...
        self.referrer = ...

        # response
        self.error_msg = ""

        self.dispatch_post_method_name = [
            # Add names in daughter classes
        ]

        # log_funcs.set_info_log(self.ip, '001', 'info', 'Open raw file')
        # print(f"{self.ip}, {self.request}")

    def setup(self, request, *args, **kwargs):
        if hasattr(self, "get") and not hasattr(self, "head"):
            self.head = self.get
        self.method = request.method
        self.request = request
        self.ip = get_ip(request)
        self.device = get_device(request)
        self.user_id = request.COOKIES.get("anonymous_user_id")
        self.handler = self.http_method_not_allowed  # Default
        messages.set_level(self.request, 10)  # write debug level
        # url
        self.referrer = urlparse(request.META.get('HTTP_REFERER', ''))

        # post flag
        try:
            self.flag = kwargs.get('flag', request.POST.get('flag'))
        except TooManyFilesSent as e:
            messages.error(request, e)
            return JsonResponse({}, status=400)

        # fingerprint
        try:
            self.fingerprint = request.POST.get('fingerprint')
        except (Exception, BaseException):
            pass

        # Ajax request, json type content, flag is included in body
        try:
            self.body = ap.smp.json.loads(request.body.decode('utf-8'))
        except (Exception, BaseException):
            pass
        else:
            try:
                self.cache_key = str(self.body['cache_key'])
                self._cache_key = f"user:{self.user_id}:data:{self.cache_key}:obj"
                self.sample = pickle.loads(cache.get(self._cache_key, default=pickle.dumps(ap.smp.Sample())))
                touch_cache(self._cache_key)  # Update cache time
            except KeyError:
                pass
            # content
            try:
                self.content = self.body['content']
            except KeyError:
                pass

    def dispatch(self, request, *args, **kwargs):
        if self.flag and self.flag in self.dispatch_post_method_name:
            return self.post(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.flag:
            self.handler = getattr(self, self.flag.lower(), self.flag_not_matched)
        print("post: %s" % self.handler.__name__)
        return self.handling(self.handler, request, *args, **kwargs)

    def flag_not_matched(self, request, *args, **kwargs):
        print(f'flag_not_matched: {self.flag}')
        pass

    def handling(self, func, request, *args, **kwargs):
        method = func.__name__
        path = request.path
        log_funcs.write_log(self.ip, 'INFO', f"Received request: {method}, {path}")
        return func(request, *args, **kwargs)

    def JsonResponse(self, data, status=200, **kwargs):
        if self.error_msg != "":
            status = 403
        self.write_log()
        return JsonResponse(data, status=status, **kwargs)

    def FileResponse(self, *args, **kwargs):
        return FileResponse(*args, **kwargs)

    def redirect(self, view_name):
        self.write_log()
        return redirect(view_name)

    def render(self, request, view_name, *args, **kwargs):
        self.write_log()
        return render(request, view_name, *args, **kwargs)

    def write_log(self, msg: str = None, level: str = "Info", **kwargs):
        if msg is not None:
            return log_funcs.write_log(self.ip, level, msg, kwargs)
        try:
            kwargs.update({"sample_name": self.sample.name()})
        except (Exception, BaseException):
            pass
        for msg in messages.get_messages(self.request):
            log_funcs.write_log(self.ip, msg.level, msg.message, **kwargs)
