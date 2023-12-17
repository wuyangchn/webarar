from django.shortcuts import render
from programs import http_funcs
# import programs.ararpy as ap
import ararpy as ap
# Create your views here.


def main_view(request):
    print(http_funcs.get_lang(request))
    return render(request, 'doc.html')


def doc_en(request):
    return render(request, 'doc.html')


def doc_zh(request):
    return render(request, 'doc.html')
