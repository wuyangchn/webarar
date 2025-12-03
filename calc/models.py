from django.db import models


class CalcRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    user = models.CharField("USER_UUID", max_length=64)
    # 新建者的ip地址
    ip = models.GenericIPAddressField("IP")
    # 新建者的设备信息地址
    device = models.CharField("HTTP_USER_AGENT", max_length=1000)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    # 文件名
    file_path = models.CharField("FILE_NAME", max_length=1000, null=True)
    # uuid
    cache_key = models.CharField("CACHE_KEY", max_length=64, null=True)


class IrraParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=True)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", unique=True, max_length=64, null=False)
    #
    pin = models.CharField("PIN", max_length=64, null=False)
    # 文件路径
    file_path = models.CharField("FILE_PATH", max_length=1000, null=False)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)


class CalcParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=True)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", unique=True, max_length=64, null=False)
    #
    pin = models.CharField("PIN", max_length=64, null=False)
    # password = encrypt(models.CharField("PASSWORD", max_length=128))
    # 文件路径
    file_path = models.CharField("FILE_PATH", max_length=1000, null=False)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)


class SmpParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=False)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", unique=True, max_length=64, null=False)
    #
    pin = models.CharField("PIN", max_length=64, null=False)
    # password = encrypt(models.CharField("PASSWORD", max_length=128))
    # 文件路径
    file_path = models.CharField("FILE_PATH", max_length=1000, null=False)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)


class ThermoParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=False)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", unique=True, max_length=64, null=False)
    #
    pin = models.CharField("PIN", max_length=64, null=False)
    # password = encrypt(models.CharField("PASSWORD", max_length=128))
    # 文件路径
    file_path = models.CharField("FILE_PATH", max_length=1000, null=False)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)


class InputFilterParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=False)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", unique=True, max_length=64, null=False)
    #
    pin = models.CharField("PIN", max_length=64, null=False)
    # password = encrypt(models.CharField("PASSWORD", max_length=128))
    # 文件路径
    file_path = models.CharField("FILE_PATH", max_length=1000, null=False)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)


class ExportPdfParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=False)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", unique=True, max_length=64, null=False)
    #
    pin = models.CharField("PIN", max_length=64, null=False)
    # password = encrypt(models.CharField("PASSWORD", max_length=128))
    # 文件路径
    file_path = models.CharField("FILE_PATH", max_length=1000, null=False)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)


class DBStandards(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=False)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", max_length=64, null=True)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)
    #
    material = models.CharField("MATERIAL", max_length=32, null=True)
    location = models.CharField("LOCATION", max_length=32, null=True)
    age = models.CharField("AGE", max_length=32, null=True)
    age_error = models.CharField("AGE_ERROR", max_length=32, null=True)
    arp = models.CharField("ARP", max_length=32, null=True)
    arp_error = models.CharField("ARP_ERROR", max_length=32, null=True)
    kp = models.CharField("KP", max_length=32, null=True)
    kp_error = models.CharField("KP_ERROR", max_length=32, null=True)
    arrp = models.CharField("ARRP", max_length=32, null=True)
    arrp_error = models.CharField("ARRP_Error", max_length=32, null=True)
    papers = models.CharField("PAPERS", max_length=1000, null=True)
    info = models.CharField("INFO", max_length=1000, null=True)


class DBInstruments(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=False)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", max_length=64, null=True)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)
    #
    manufacturer = models.CharField("MANUFACTURER", max_length=32, null=True)
    cup_structure = models.CharField("CUP_STRUCTURE", max_length=32, null=True)
    amplifier = models.CharField("AMPLIFIER", max_length=32, null=True)
    sensitivity = models.CharField("SENSITIVITY", max_length=32, null=True)
    resolution = models.CharField("RESOLUTION", max_length=32, null=True)
    papers = models.CharField("PAPERS", max_length=1000, null=True)
    info = models.CharField("INFO", max_length=1000, null=True)


class DBLaboratories(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 新建者的ip地址
    ip = models.CharField("IP", max_length=64, null=False)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    name = models.CharField("NAME", max_length=64, null=True)
    #
    uploader_email = models.EmailField('UPLOADER_EMAIL', max_length=64, null=True)
    #
    country = models.CharField("COUNTRY", max_length=32, null=True)
    city = models.CharField("CITY", max_length=32, null=True)
    manager = models.CharField("MANAGER", max_length=32, null=True)
    instruments = models.CharField("INSTRUMENTS", max_length=500, null=True)
    papers = models.CharField("PAPERS", max_length=1000, null=True)
    info = models.CharField("INFO", max_length=1000, null=True)


class ReceivedFiles(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.CharField("USER_UUID", max_length=64)
    # ip地址
    ip = models.GenericIPAddressField("IP")
    # 服务器文件地址
    file_path = models.CharField("FILE_PATH", max_length=1000, null=True)
    # 原始文件名
    original_name = models.CharField("FILE_NAME", max_length=1000, null=True)
    # 自动记录插入时间
    insert_time = models.DateTimeField("INSERT_TIME", auto_now_add=True)
    # 自动记录更新时间
    update_time = models.DateTimeField("UPDATE_TIME", auto_now=True)
    #
    deleted = models.BooleanField('DELETED', null=True)
    # 删除时间
    deleted_time = models.DateTimeField("DELETED_TIME", auto_now=False, null=True)


