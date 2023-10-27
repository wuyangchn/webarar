"""
封装MySql数据库方法，如存入和读取等
"""
import decimal
import os
import traceback
from django.conf import settings
from calc import models as calc_models
from . import http_funcs, samples
import pymysql
from django.views.decorators.csrf import csrf_exempt

convert_func = {
    'BigAutoField': int,
    'IntegerField': int,
    'CharField': str,
    'DecimalField': decimal.Decimal
}


def get_sql_content(table):
    data = []
    for i in table.objects.all().values_list():
        row = []
        for j in range(len(i) - 1):
            if isinstance(i[j + 1], str):
                row.append(str(i[j + 1]))
            elif isinstance(i[j + 1], decimal.Decimal):
                row.append(float(i[j + 1]))
            elif isinstance(i[j + 1], int):
                row.append(int(i[j + 1]))
            else:
                row.append('')
        data.append(row)
    print(data)
    return data


def save_new_table(new_data, table):
    # 清空数据表
    id_list = table.objects.all().values_list('id', flat=True)
    for id in id_list:
        table.objects.filter(id=id).delete()
    print('已清空数据表')
    # 使数据表id重新从0开始
    conn = pymysql.connect(
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        database=settings.DATABASES['default']['NAME'],
        port=settings.DATABASES['default']['PORT']
    )
    cursor = conn.cursor()
    cursor.execute('select * from calc_%s;' % table.__name__)
    cursor.execute('set foreign_key_checks=0')
    cursor.execute('truncate table calc_%s;' % table.__name__)
    cursor.execute('set foreign_key_checks=1')
    cursor.close()
    conn.close()
    # 读取传递的数据，去除后面的空列表
    k = list(this_list_is_empty(i) for i in new_data)
    k.reverse()
    if False in k:
        new_data.reverse()
        new_data: list = new_data[k.index(False):]
        new_data.reverse()
    else:
        new_data = []
    # 保存到数据表
    field_names = [field.name for field in table._meta.get_fields()]  # 获取数据表的字段名
    field_classes = [field.__class__.__name__ for field in table._meta.get_fields()]  # 获取数据表的字段类型
    for each_row in new_data:
        if this_list_is_empty(each_row):
            table.objects.create()
        else:
            content = dict()
            for i in range(len(field_names) - 1):
                try:
                    content[field_names[i+1]] = convert_func[field_classes[i+1]](each_row[i])
                except (IndexError, decimal.InvalidOperation):
                    continue
                except TypeError:
                    if isinstance(each_row[i], type(None)):
                        continue
                    else:
                        raise BaseException
                except (Exception, BaseException) as e:
                    print(traceback.format_exc())
                    continue
            table.objects.create(**content)
    print('保存当前表格数据到数据表')


def this_list_is_empty(a):
    if not isinstance(a, list) or a == []:
        return True
    for i in a:
        if i not in ['', None]:
            return False
    return True

