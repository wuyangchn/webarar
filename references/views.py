
from django.http import JsonResponse

from home import models as home_models
from . import models
from django.shortcuts import render
# from django.conf import settings
import requests
from bs4 import BeautifulSoup
import time
import random

from programs import basic_funcs, http_funcs, log_funcs, ap


# Create your views here.


def references(request):
    return render(request, 'references.html')


def journal_ranking(request):
    # 记录访问
    if basic_funcs.is_ajax(request):
        user_id = request.COOKIES.get("anonymous_user_id")
        http_funcs.set_user_sql(request, home_models.User, user_id)
        return JsonResponse({})
    # disciplines = [
    #     '信息与通信工程', '物理学', '土木工程', '水利工程', '环境科学与工程', '机械工程', '工商管理', '安全科学与工程', '地质资源与地质工程（资源）', '地球物理学',
    #     '管理科学与工程', '数学', '外国语言文学', '新闻传播学', '计算机科学与技术', '地理科学', '法学', '马克思主义理论', '设计学', '教育学',
    #     '地质资源与地质工程（勘察地球物理）', '化学', '石油与天然气工程', '公共管理', '材料科学与工程', '地质资源与地质工程（工程地质）', '大气科学', '地质学', '软件工程',
    #     '海洋科学', '体育学', '心理学', '测绘科学与技术', '生物学', '地质资源与地质工程（岩土钻掘）', '地质资源与地质工程（地球信息）', '控制科学与工程', '应用经济学'
    # ]
    #
    # def isRenwen(s):
    #     return s in [
    #         '体育学', '公共管理', '外国语言文学', '工商管理', '应用经济学', '心理学', '教育学', '新闻传播学', '法学',  '管理科学与工程', '设计学', '马克思主义理论'
    #     ]

    # JIF21_list = ap.files.xls.open_xls(os.path.join(settings.STATICFILES_DIRS[0], f'document/JCR_JIF_2021.xls'))
    # JIF21_list = JIF21_list['JCR_JIF_2021'][1:]
    # JIF21_dict = {}
    # JIF22_list = ap.files.xls.open_xls(os.path.join(settings.STATICFILES_DIRS[0], f'document/JCR_JIF_2022.xls'))
    # JIF22_list = JIF22_list['JCR_JIF_2022'][1:]
    # JIF22_dict = {}
    # JIF23_list = ap.files.xls.open_xls(os.path.join(settings.STATICFILES_DIRS[0], f'document/JCR_JIF_2023.xls'))
    # JIF23_list = JIF23_list['JCR_JIF_2023'][1:]
    # JIF23_dict = {}
    # import os
    # JIF24_list = ap.files.xls.open_xls(os.path.join(settings.STATICFILES_DIRS[0], f'document/JCR_JIF_2024.xls'))
    # JIF24_list = JIF24_list['JCR_JIF_2024'][1:]
    # JIF24_dict = {}
    # JIF24_dict = {
    #     "STATISTICAL ANALYSIS AND DATA MINING": 3.6,
    #     "JOURNAL OF DATABASE MANAGEMENT": 0.8,
    #     "INTERNATIONAL JOURNAL OF OIL GAS AND COAL TECHNOLOGY": 0.7,
    # }
    # for journal in JIF21_list:
    #     JIF21_dict.update({str(journal[0]).upper(): journal})
    # for journal in JIF22_list:
    #     JIF22_dict.update({str(journal[0]).upper(): journal})
    # for journal in JIF23_list:
    #     JIF23_dict.update({str(journal[0]).upper(): journal})
    # for journal in JIF24_list:
    #     JIF24_dict.update({str(journal[1]).upper(): journal})
    #
    # for key, values in JIF24_dict.items():
    #     for journal in models.CUGJournalRanking.objects.filter(full_name__iexact=str(key).upper()):
    #         journal.jif24 = values
    #         journal.save()
    #     for journal in models.Journal.objects.filter(full_name__iexact=str(key).upper()):
    #         journal.jif24 = values
    #         journal.save()

    # def get_diff(a, b):
    #     try:
    #         diff = round(float(b) - float(a), 2)
    #         return f"+ {abs(diff)}" if diff >= 0 else f"- {abs(diff)}"
    #     except:
    #         return 'N/A'
    # data = []
    # for cug_journal in models.CUGJournalRanking.objects.all():
    #     cug_journal.tag = '人文社科类' if isRenwen(cug_journal.subject) else '理工类' if cug_journal.subject in disciplines else "N/A"
    #     cug_journal.save()
    #     journal_record = models.Journal.objects.filter(full_name__iexact=str(cug_journal.full_name)).first()
    #     if journal_record is not None:
    #         cug_journal.jif21 = journal_record.jif21
    #         cug_journal.jif22 = journal_record.jif22
    #         cug_journal.jif23 = journal_record.jif23
    #         cug_journal.short_name = journal_record.short_name
    #         cug_journal.issn = journal_record.issn
    #         cug_journal.eissn = journal_record.eissn
    #         cug_journal.tag = '人文社科类' if isRenwen(cug_journal.subject) else '理工类'
    #         cug_journal.save()
    #         jifs = [journal_record.jif21, journal_record.jif22, journal_record.jif23]
    #     else:
    #         jifs = ["N/A", "N/A", "N/A"]
    #     data.append({
    #         'journal': cug_journal.full_name, 'tier': cug_journal.tier,
    #         'discipline': cug_journal.subject, 'tag': cug_journal.tag,
    #         'IF21': jifs[0], 'IF22': jifs[1], 'IF23': jifs[2],
    #         'Diff': get_diff(jifs[1], jifs[2])
    #     })
    # for journal in models.CUGJournalRanking.objects.all():
    #     if ord(journal.full_name[0]) > 125:
    #         continue
    #     if journal.letpub_id != 0 and '&' not in journal.full_name:
    #         continue
    #     # if journal.full_name.upper() != 'LASER & PHOTONICS REVIEWS':
    #     #     continue
    #     res = requests.get(f'https://www.letpub.com.cn/journalappAjaxXS.php?querytype=autojournal&term={journal.full_name}')
    #     if res.status_code == 200:
    #         data_list = json.loads(res.text)
    #         if len(data_list) == 0:
    #             continue
    #         for data in data_list:
    #             if data['label'].upper() == journal.full_name.upper():
    #                 print(f"{journal.full_name = }, {journal.issn = }, {data = }")
    #                 jid = data['id']
    #                 journal.letpub_id = int(jid)
    #                 if journal.issn == data_list[0]['issn']:
    #                     journal.issn = data['issn']
    #                 journal.save()
    #                 break

    # i = 0
    # for journal in models.CUGJournalRanking.objects.all():
    #     i += 1
    #     if journal.tag == "人文社科类":
    #         continue
    #     if journal.tier not in ['T4', 'T5', 'T6']:
    #         continue
    #     headers = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    #     }
    #
    #     if journal.xinrui_id != "N/A" and len(journal.xinrui_id) == 5:
    #         continue
    #     else:
    #         journal.xinrui_id = "N/A"
    #         x = requests.get(f'https://www.xr-scholar.com/Journals/Search?year=2026&keyword=' + journal.full_name, headers=headers, timeout=20)
    #         if x.status_code == 200:
    #             try:
    #                 soup = BeautifulSoup(x.text, 'html.parser')
    #                 res = soup.find('table', class_='table table-vcenter card-table').find('a', class_='text-reset fw-bold')
    #                 href = res.get('href')[-5:]
    #             except:
    #                 continue
    #             else:
    #                 journal.xinrui_id = href
    #             print(f"{i}, {journal.full_name}, {journal.xinrui_id}, {journal.xinrui_tier}, {journal.xinrui_top}")
    #
    #         time.sleep(random.uniform(0.2, 0.6))
    #
    #     # if journal.xinrui_tier.startswith('T') or journal.xinrui_id == 'N/A':
    #     #     continue
    #     # else:
    #     #     x = requests.get(r'https://www.xr-scholar.com/Journals/' + journal.xinrui_id, headers=headers, timeout=100)
    #     #     if x.status_code == 200:
    #     #         try:
    #     #             soup = BeautifulSoup(x.text, 'html.parser')
    #     #             tbody = soup.find('table', class_='table table-vcenter table-bordered card-table text-center mb-0').find('tbody')
    #     #             tier = tbody.find('span', class_=lambda cc: cc and 'xr-tier-badge' in cc and 'journal-tier-badge-wrap' in cc).text
    #     #             top = tbody.find('span', class_=lambda cc: cc and 'xr-tier-top' in cc or 'text-muted' in cc).text
    #     #         except:
    #     #             continue
    #     #         else:
    #     #             journal.xinrui_tier = f"T" + re.search(r'\d+', tier).group()
    #     #             journal.xinrui_top = "top" in top.lower()
    #     #
    #     #     time.sleep(random.uniform(0.2, 6))
    #
    #     # print(f"{i}, {journal.full_name}, {journal.xinrui_id}, {journal.xinrui_tier}, {journal.xinrui_top}")
    #     journal.save()

    data = list(models.CUGJournalRanking.objects.values(
        'full_name', 'tier', 'subject', 'tag', 'jif21', 'jif22', 'jif23', 'jif24',
        'letpub_id', 'xinrui_id', 'xinrui_tier', 'xinrui_top'))

    def neg_jif(jif):
        if isinstance(jif, str) and not jif.isprintable():
            jif = ''.join(x for x in jif if x.isprintable())
        try:
            return -float(jif)
        except:
            return 0
    data.sort(key=lambda x: (x['tier'], neg_jif(x['jif24'])))
    log_funcs.write_log(basic_funcs.get_ip(request), 'info', 'Visit journal ranking html')

    if not home_models.User.objects.filter(uuid=str('--journalrankingvisitorcounter--')).exists():
        home_models.User.objects.create(
            uuid=str('--journalrankingvisitorcounter--'),
            ip='127.0.0.1',
            device='N/A',
            count=1
        )
    if not home_models.User.objects.filter(uuid=str('--journalrankinglikercounter--')).exists():
        home_models.User.objects.create(
            uuid=str('--journalrankinglikercounter--'),
            ip='127.0.0.1',
            device='N/A',
            count=1
        )
    _user = home_models.User.objects.get(uuid=str('--journalrankingvisitorcounter--'))
    _user.count = _user.count + 1
    _user.save()

    return render(request, 'journal_ranking.html', {
        'data': ap.smp.json.dumps(data),
        'total_count': _user.count,
        'zan_count': home_models.User.objects.get(uuid=str('--journalrankinglikercounter--')).count, })


def new_liker(request):
    if not home_models.User.objects.filter(uuid=str('--journalrankinglikercounter--')).exists():
        home_models.User.objects.create(
            uuid=str('--journalrankinglikercounter--'),
            ip='127.0.0.1',
            device='N/A',
            count=1
        )
    _user = home_models.User.objects.get(uuid=str('--journalrankinglikercounter--'))
    _user.count = _user.count + 1
    _user.save()
    return JsonResponse({"status": "success"})


def api_callback(request):
    return journal_ranking(request)

