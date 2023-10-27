import json
import os

from django.shortcuts import render
from programs import file_funcs, calc_funcs
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import traceback

# Create your views here.


def detail(request):
    return render(request, 'detail.html')

def lov_view(request):
    return render(request, 'heating_log.html')

def experiment_log(request):
    file = request.FILES.get(str(0))
    res = ''
    try:
        web_file_path, file_name, suffix = file_funcs.get_post_file(file, settings.UPLOAD_ROOT)
    except (Exception, BaseException) as e:
        msg = f"{file} is not supported. "
    else:
        with open(web_file_path, 'rb') as f:
            res = f.read().decode('utf-8')
    try:
        data = get_log_data(res)
    except Exception:
        print(traceback.format_exc())
        data = []
    res = ''  # no need to return content
    return JsonResponse({'text': res, 'data': data})

def get_log_data(text: str):
    import re
    data = [[], []]
    text = text.split('\n')
    for line in text:
        try:
            datetime, sp, ap = re.findall("(.*)Z;(.*);(.*)\r", line)[0]
        except:
            pass
        else:
            # datetime = calc_funcs.get_datetime(y, m, d, h, m, s, base=[1988, 9, 3, 0, 0]) * 1000
            data[0].append([datetime, sp])
            data[1].append([datetime, ap])
    return data

def updating_log(request):
    text = json.loads(request.body.decode('utf-8'))['text']
    filename = json.loads(request.body.decode('utf-8'))['filename']
    if filename == "":
        filename = 'inside_temeprature_log'
    filepath = os.path.join(settings.SETTINGS_ROOT, f'{filename}.log')
    with open(filepath, 'w') as f:
        f.write(text)
    # file_funcs.save_txt_file(filepath, text)
    return JsonResponse({})