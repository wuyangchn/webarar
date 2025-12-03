from django.contrib import admin
from .models import CalcRecord, CalcParams, IrraParams, SmpParams, InputFilterParams, ThermoParams, ExportPdfParams, \
    DBInstruments, DBLaboratories, DBStandards, ReceivedFiles

# Register your models here.


class CalcRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ip', 'device', 'file_path', 'cache_key', 'insert_time', 'update_time')
    search_fields = ('ip',)
    readonly_fields = ('insert_time', 'update_time')


class ParamsAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip', 'name', 'pin', 'file_path', 'uploader_email', 'insert_time', 'update_time')
    search_fields = ('name',)


class ArArDBInsAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip', 'name', 'insert_time', 'update_time', 'uploader_email', 'manufacturer', 'cup_structure',
                    'amplifier', 'sensitivity', 'resolution', 'papers', 'info')
    search_fields = ('name',)


class ArArDBLabAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip', 'name', 'insert_time', 'update_time', 'uploader_email', 'country', 'city',
                    'manager', 'instruments', 'papers', 'info')
    search_fields = ('name',)


class ArArDBStdAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip', 'name', 'insert_time', 'update_time', 'uploader_email', 'material', 'location',
                    'age', 'age_error', 'arp', 'arp_error', 'kp', 'kp_error', 'arrp', 'arrp_error', 'papers', 'info')
    search_fields = ('name',)


class FilesOnServerDB(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'ip', 'file_path', 'original_name', 'insert_time', 'update_time', 'deleted',
                    'deleted_time')
    search_fields = ('uuid', 'file_path', 'name',)


admin.site.register(CalcRecord, CalcRecordAdmin)
admin.site.register(CalcParams, ParamsAdmin)
admin.site.register(IrraParams, ParamsAdmin)
admin.site.register(SmpParams, ParamsAdmin)
admin.site.register(InputFilterParams, ParamsAdmin)
admin.site.register(ThermoParams, ParamsAdmin)
admin.site.register(ExportPdfParams, ParamsAdmin)
admin.site.register(DBInstruments, ArArDBInsAdmin)
admin.site.register(DBLaboratories, ArArDBLabAdmin)
admin.site.register(DBStandards, ArArDBStdAdmin)
admin.site.register(ReceivedFiles, FilesOnServerDB)

