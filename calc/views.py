import copy
import os
import json
import pickle
import traceback
import re
import numpy as np
import uuid
import time
import itertools

# from math import ceil
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache

from . import models
from programs import http_funcs, ap
from programs.log_funcs import debug_print


# Create your views here.
class CalcHtmlView(http_funcs.ArArView):
    """
    Views on calc.html, responses to command of opening files based on flags.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
            "open_raw_file",
            "open_arr_file",
            "open_full_xls_file",
            "open_age_file",
            "open_current_file",
            "open_new_file",
            "open_multi_files",
            "update_sample_photo"
        ]

    def open_raw_file(self, request, *args, **kwargs):
        return self.redirect('open_raw_file_filter')

    def open_arr_file(self, request, *args, **kwargs):
        web_file_path, file_name, extension = \
            ap.files.basic.upload(request.FILES.get('arr_file'), settings.UPLOAD_ROOT)
        messages.info(request, f'Uploaded file: {web_file_path}')
        try:
            sample = ap.from_arr(web_file_path)
        except (Exception, BaseException) as e:
            debug_print(traceback.format_exc())
            messages.error(request, f"Open arr failed: {e}. {file_name = }")
            return self.render(request, 'calc.html')
        else:
            return self.render(request, 'object.html', http_funcs.open_object_file(request, sample, web_file_path))

    def open_full_xls_file(self, request, *args, **kwargs):
        try:
            web_file_path, file_name, extension = \
                ap.files.basic.upload(request.FILES.get('full_xls_file'), settings.UPLOAD_ROOT)
            messages.info(request, f'Uploaded file: {web_file_path}')
            file_name = file_name if '.full' not in file_name else file_name.split('.full')[0]
            sample = ap.from_full(file_path=web_file_path, sample_name=file_name)
            sample.recalculate(re_plot=True, re_plot_style=True, re_set_table=True, re_table_style=True)
        except (Exception, BaseException) as e:
            messages.error(request, e)
            return self.render(request, 'calc.html')
        else:
            return self.render(request, 'object.html', http_funcs.open_object_file(request, sample, web_file_path))

    def open_age_file(self, request, *args, **kwargs):
        try:
            web_file_path, sample_name, extension = \
                ap.files.basic.upload(request.FILES.get('age_file'), settings.UPLOAD_ROOT)
            messages.info(request, f'Uploaded file: {web_file_path}')
            sample = ap.from_age(file_path=web_file_path, sample_name=sample_name)
            try:
                # Re-calculating ratio and plot after reading age or full files
                sample.recalculate(re_calc_ratio=True, re_plot=True, re_plot_style=True, re_set_table=True)
                # ap.recalculate(sample, re_calc_ratio=True, re_plot=True, re_plot_style=True, re_set_table=True)
            except Exception as e:
                messages.error(request, e)
                debug_print(f'Error in setting plot: {traceback.format_exc()}')
        except (Exception, BaseException) as e:
            debug_print(traceback.format_exc())
            messages.error(request, e)
            return self.render(request, 'calc.html')
        else:
            return self.render(request, 'object.html', http_funcs.open_object_file(request, sample, web_file_path))

    def open_current_file(self, request, *args, **kwargs):
        return self.render(request, 'object.html', http_funcs.open_last_object(request))

    def open_new_file(self, request, *args, **kwargs):
        sample = ap.from_empty()
        return self.render(request, 'object.html', http_funcs.open_object_file(request, sample, web_file_path=''))

    def open_multi_files(self, request, *args, **kwargs):
        length = int(request.POST.get('length'))
        messages.info(request, f"{length} files uploaded")
        files = {}
        for i in range(length):
            file = request.FILES.get(str(i))
            try:
                web_file_path, file_name, suffix = ap.files.basic.upload(
                    file, settings.UPLOAD_ROOT)
                messages.info(request, f'Uploaded file: {web_file_path}')
            except (Exception, BaseException) as e:
                messages.error(request, e)
                continue
            else:
                files.update({f"multi_files_{i}": {'name': file_name, 'path': web_file_path, 'suffix': suffix}})
        response = HttpResponse(content_type="text/html; charset=utf-8", status=299)
        contents = []
        for key, file in files.items():
            handler = {
                '.arr': ap.from_arr, '.xls': ap.from_full, '.age': ap.from_age
            }.get(file['suffix'], None)
            try:
                if handler:
                    sample = handler(file['path'], **{'file_name': file['name']})
                else:
                    raise TypeError(f"File type {file['suffix']} is not supported: {file['name']}")
            except (Exception, BaseException) as e:
                messages.error(request, e)
                debug_print(traceback.format_exc())
                continue
            else:
                contents.append(self.render('object.html', http_funcs.open_object_file(request, sample, web_file_path=file['path'])).component)
        response.writelines(contents)
        return response

    def get(self, request, *args, **kwargs):
        # Render calc.html when users are visiting /calc.
        return self.render(request, 'calc.html')

    def flag_not_matched(self, request, *args, **kwargs):
        # Show calc.html when the received flag doesn't exist.
        messages.error(request, f"{self.flag}, it is not matched")
        return self.render(request, 'calc.html')


class ButtonsResponseObjectView(http_funcs.ArArView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
        ]

    def get(self, request, *args, **kwargs):
        # Visiting /calc/object
        return self.render(request, 'object.html', http_funcs.open_last_object(request))

    def update_sample_photo(self, request, *args, **kwargs):
        file = request.FILES.get('picture')
        web_file_path, name, suffix = ap.files.basic.upload(file, os.path.join(settings.STATICFILES_DIRS[0], 'upload'))
        messages.info(request, f"Uploaded picture: {web_file_path}")
        return self.JsonResponse({'picture': settings.STATIC_URL + 'upload/' + file.name})

    def get_auto_scale(self, request, *args, **kwargs):
        figure_id = self.body['figure_id']
        xscale, yscale = ap.smp.style.reset_plot_scale(smp=self.sample, only_figure=figure_id)
        return self.JsonResponse({
            'status': 'success', 'xMin': xscale[0], 'xMax': xscale[1], 'xInterval': xscale[2],
            'yMin': yscale[0], 'yMax': yscale[1], 'yInterval': yscale[2]
        })

    def update_components_diff(self, request, *args, **kwargs):
        diff = dict(self.body['diff'])
        self.write_log(f"Update components diff, keys of difference: {list(diff.keys())}")
        for name, attrs in diff.items():
            ap.smp.basic.update_object_from_dict(
                ap.smp.basic.get_component_byid(self.sample, name), attrs)

        self.sample.SequenceName = [v[0] for i, v in enumerate(self.sample.IsochronsTable.data)]
        self.sample.SequenceValue = [v[1] for i, v in enumerate(self.sample.IsochronsTable.data)]
        self.sample.IsochronMark = [v[2] for i, v in enumerate(self.sample.IsochronsTable.data)]

        ap.smp.table.update_data_from_table(self.sample)

        # self.sample.UnknownTable.data = ap.calc.arr.transpose(self.sample.UnknownTable.data)
        # self.sample.BlankTable.data = ap.calc.arr.transpose(self.sample.BlankTable.data)
        # self.sample.CorrectedTable.data = ap.calc.arr.transpose(self.sample.CorrectedTable.data)
        # self.sample.DegasPatternTable.data = ap.calc.arr.transpose(self.sample.DegasPatternTable.data)
        # self.sample.PublishTable.data = ap.calc.arr.transpose(self.sample.PublishTable.data)
        # self.sample.AgeSpectraPlot.data = ap.calc.arr.transpose(self.sample.AgeSpectraPlot.data)
        # self.sample.IsochronsTable.data = ap.calc.arr.transpose(self.sample.IsochronsTable.data)
        # self.sample.TotalParamsTable.data = ap.calc.arr.transpose(self.sample.TotalParamsTable.data)

        res = {}
        if 'figure_9' in diff.keys() and not all(
                [i not in diff.get('figure_9').keys() for i in ['set1', 'set2', 'set3']]):
            # Backup after changes are applied
            components_backup = copy.deepcopy(ap.smp.basic.get_components(self.sample))
            # Histogram plot, replot is required
            ap.smp.plots.recalc_agedistribution(self.sample)
            res = ap.smp.basic.get_diff_smp(backup=components_backup, smp=ap.smp.basic.get_components(self.sample))

        self.sample.sequence()

        http_funcs.create_cache(self.sample, self.cache_key)  # Update cache
        return self.JsonResponse(res)

    def click_points_update_figures(self, request, *args, **kwargs):

        clicked_data = self.content['clicked_data']
        current_set = self.content['current_set']
        auto_replot = self.content['auto_replot']
        figures = self.content.pop('figures',
                                   ['figure_2', 'figure_3', 'figure_4', 'figure_5', 'figure_6', 'figure_7', ])
        sample = self.sample
        components_backup = copy.deepcopy(ap.smp.basic.get_components(sample))
        # debug_print(f"{sample.IsochronMark = }")

        data_index = clicked_data[-1] - 1  # Isochron plot data label starts from 1, not 0
        sample.set_selection(data_index, [1, 2][current_set == "set2"])

        if auto_replot:
            # Re-plot after clicking points
            sample.recalculate(re_plot=True, isInit=False, isIsochron=True, isPlateau=False, figures=figures)
            # ap.recalculate(sample, re_plot=True, isInit=False, isIsochron=True, isPlateau=True)

        # Response are changes in sample.Components, in this way we can decrease the size of response.
        res = ap.smp.basic.get_diff_smp(
            backup=components_backup, smp=ap.smp.basic.get_components(sample))
        # Update isochron table data, changes in isotope table is not required to transfer
        ap.smp.table.update_table_data(sample, only_table='7')
        http_funcs.create_cache(sample, self.cache_key)  # 更新缓存
        # debug_print(f"在点击事件结束之后 {sample.IsochronMark = }")

        return self.JsonResponse({'res': ap.smp.json.dumps(res)})

    def update_handsontable(self, request, *args, **kwargs):
        btn_id = str(self.body['btn_id'])
        recalculate = self.body['recalculate']  # This is always False
        data = self.body['data']
        sample = self.sample
        messages.info(request, f'Updating handsontable, btn id: {btn_id}')
        # backup for later comparision
        components_backup = copy.deepcopy(ap.smp.basic.get_components(sample))
        try:
            if btn_id == '0':  # 实验信息
                ap.smp.basic.update_plot_from_dict(sample.Info, data)
                messages.info(request, f'Update completed, btn id: {btn_id}')
            else:
                data = ap.calc.arr.remove_empty(data)
                if len(data) == 0:
                    raise ValueError("The length of data list must be greater than 0")
                sample.update_table(data, btn_id)
                if btn_id == '7':
                    # Re-calculate isochron and plateau data, and replot.
                    # Re-calculation will not be applied automatically when other tables were changed
                    messages.info(request, f'Recalculating, btn id: {btn_id}, '
                                           f're_plot=True, isInit=False, isIsochron=True, isPlateau=True')
                    sample.recalculate(re_plot=True, isInit=False, isIsochron=True, isPlateau=True)
                    messages.info(request, f'Recalculation completed')
                    # ap.recalculate(sample, re_plot=True, isInit=False, isIsochron=True, isPlateau=True)

        except Exception as e:
            debug_print(traceback.format_exc())
            messages.error(request, e)
            return self.JsonResponse({'msg': f'Error: {e}'}, status=403)

        http_funcs.create_cache(sample, self.cache_key)  # Update cache
        res = ap.smp.basic.get_diff_smp(components_backup, ap.smp.basic.get_components(sample))
        messages.info(request, f"Keys of difference: {list(res.keys())}")
        return self.JsonResponse({'changed_components': ap.smp.json.dumps(res)})

    def get_regression_result(self, request, *args, **kwargs):
        data = list(self.body.get('data'))
        method = str(self.body.get('method'))
        adjusted_x = list(self.body.get('x'))

        x, adjusted_time = [], []
        year, month, day, hour, min, second = re.findall(r"\d+", data[0][0])[0]
        for each in data[0]:
            x.append(ap.calc.basic.get_datetime(
                *re.findall(r"\d+", each)[0],
                base=[int(year), int(month), int(day), int(hour), int(min)]
            ))
        for each in adjusted_x:
            adjusted_time.append(ap.calc.basic.get_datetime(*re.findall(r"\d+", each)[0],
                base=[int(year), int(month), int(day), int(hour), int(min)]
            ))
        y = data[1]
        x, y = zip(*sorted(zip(x, y), key=lambda _x: _x[0]))
        handler = {
            'linear': ap.calc.regression.linest,
            'average': ap.calc.regression.average,
            'quadratic': ap.calc.regression.quadratic,
            'polynomial': ap.calc.regression.polynomial,
            'power': ap.calc.regression.power,
            'exponential': ap.calc.regression.exponential,
        }
        if method in handler.keys():
            try:
                handler = handler[method]
                res = handler(y, x)
            except Exception as e:
                debug_print(traceback.format_exc())
                messages.error(request, e)
                res = False
            if res:
                line_data = [adjusted_x, res[7](adjusted_time)]
                return self.JsonResponse({'r2': res[3], 'line_data': line_data, 'sey': res[8]})
        return self.JsonResponse({'r2': 'None', 'line_data': [], 'sey': 'None'})

    def recalculation(self, request, *args, **kwargs):
        sample = self.sample
        checked_options = self.content['checked_options']
        others = self.content.pop('others', {})
        isochron_mark = self.content.pop('isochron_mark', False)
        # debug_print(f"Recalculation Isochron Mark = {isochron_mark}")
        debug_print(f"{others = }")
        try:
            sample.Info.preference.update({'confidenceLevel': others.get('sigma', sample.Info.preference.get('confidenceLevel', 1))})
        except Exception as e:
            pass
        if isochron_mark:
            sample.IsochronMark = isochron_mark.copy()
            sample.sequence()
        # backup for later comparision
        components_backup = copy.deepcopy(ap.smp.basic.get_components(sample))
        try:
            # Re-calculating based on selected options
            sample.recalculate(*checked_options, **others)
            # sample = ap.recalculate(sample, *checked_options)
        except Exception as e:
            debug_print(traceback.format_exc())
            messages.error(request, e)
            return self.JsonResponse({'msg': f'Error in recalculating: {e}'}, status=403)
        ap.smp.table.update_table_data(sample)  # Update data of tables after re-calculation
        # Update cache
        http_funcs.create_cache(sample, self.cache_key)
        res = ap.smp.basic.get_diff_smp(backup=components_backup, smp=ap.smp.basic.get_components(sample))
        messages.info(request, f"Recalculation completed. Keys of difference: {list(res.keys())}")
        return self.JsonResponse({'msg': "Success to recalculate", 'res': ap.smp.json.dumps(res)})

    def force_syn(self, request, *args, **kwargs):
        try:
            messages.info(request, f"Forcing syn completed")
            return self.JsonResponse({'sampleComponents': ap.smp.json.dumps(ap.smp.basic.get_components(self.sample))})
        except (Exception, BaseException) as e:
            msg = f'Error in forcing syn: {e}'
            messages.error(request, msg)
            return self.JsonResponse({'msg': msg}, status=403)

    def flag_not_matched(self, request, *args, **kwargs):
        # Show calc.html when the received flag doesn't exist.
        return self.render(request, 'object.html', http_funcs.open_last_object(request))


class RawFileView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
            "submit",
            'close',
            'to_project_view',
            'raw_data_submit',
        ]

    def get(self, request, *args, **kwargs):
        # Visiting /calc/raw
        return self.render(request, 'raw_filter.html')

    def flag_not_matched(self, request, *args, **kwargs):
        return self.redirect('calc_view')

    def close(self, request, *args, **kwargs):
        return self.redirect('calc_view')

    def raw_files_changed(self, request, *args, **kwargs):
        files = []
        names = list(models.InputFilterParams.objects.values_list('name', flat=True))
        for file in request.FILES.getlist('raw_file'):
            try:
                web_file_path, file_name, suffix = ap.files.basic.upload(
                    file, settings.UPLOAD_ROOT)
            except (Exception, BaseException) as e:
                messages.error(request, e)
                continue
            else:
                self.write_log(f"Read raw file: {web_file_path}")
                files.append({
                    'name': file_name, 'extension': suffix, 'path': web_file_path,
                    'filter': suffix[1:],
                    'filter_list': names
                })
        return self.JsonResponse({'files': files})

    def submit(self, request, *args, **kwargs):
        files = json.loads(request.POST.get('raw-file-table'))['files']
        file_path = [each['file_path'] for each in files if each['checked']]
        filter_name = [each['filter'] for each in files if each['checked']]
        print(f"{filter_name = }")
        filter_paths = [getattr(models, "InputFilterParams").objects.get(name=each).file_path for each in filter_name]
        try:
            raw = ap.smp.raw.to_raw(file_path=file_path, input_filter_path=filter_paths)
            raw.do_regression()

            allIrraNames = list(models.IrraParams.objects.values_list('name', flat=True))
            allCalcNames = list(models.CalcParams.objects.values_list('name', flat=True))
            allSmpNames = list(models.SmpParams.objects.values_list('name', flat=True))

            # update cache
            cache_key = http_funcs.create_cache(raw)
            return self.render(request, 'extrapolate.html', {
                'raw_data': ap.smp.json.dumps(raw), 'raw_cache_key': ap.smp.json.dumps(cache_key),
                'allIrraNames': allIrraNames, 'allCalcNames': allCalcNames, 'allSmpNames': allSmpNames
            })
        except FileNotFoundError as e:
            messages.error(request, e)
        except ValueError as e:
            debug_print(traceback.format_exc())
            messages.error(request, e)
        except (Exception, BaseException):
            debug_print(traceback.format_exc())
            messages.error(request, traceback.format_exc())
        return self.render(request, 'raw_filter.html')

    def raw_data_submit(self, request, *args, **kwargs):
        """
        Raw data submit, return a sample instance and render a object html.
        """
        irradiationParams = self.body['irradiationParams']
        calculationParams = self.body['calculationParams']
        sampleParams = self.body['sampleParams']
        sampleInfo = self.body['sampleInfo']
        selectedSequences = self.body['selectedSequences']
        fingerprint = self.body['fingerprint']

        raw: ap.RawData = self.sample

        # create sample
        sample = raw.to_sample(selectedSequences)

        info = {
            'sample': {'name': sampleInfo[0], 'type': sampleInfo[1], 'material': sampleInfo[2], 'location': sampleInfo[3]},
            'researcher': {'name': sampleInfo[4]},
            'laboratory': {'name': sampleInfo[5], 'info': sampleInfo[6], 'analyst': sampleInfo[7]},
            'experiment': {'name': sampleInfo[0], 'step_num': len(sample.SequenceName)}
        }
        sample.set_info(info=info)

        try:
            rows = list(range(len(sample.SequenceName)))
            sample.set_params(irradiationParams['param'], 'irra', rows)
            sample.set_params(calculationParams['param'], 'calc', rows)
            sample.set_params(sampleParams['param'], 'smp', rows)
        except (BaseException, Exception):
            debug_print(traceback.format_exc())
        try:
            sample.recalculate(*[True] * 11, False, *[True] * 4)  # Calculation after submitting row data
            # ap.recalculate(sample, *[True] * 12)  # Calculation after submitting row data
            ap.smp.table.update_table_data(sample)  # Update table after submission row data and calculation
        except (Exception, BaseException) as e:
            messages.error(request, message=f"Calculation Error: {e}")
            return self.JsonResponse({'msg': f"Calculation Error: {e}"}, status=403)
        # update cache
        cache_key = http_funcs.create_cache(sample)
        # write mysql
        http_funcs.set_mysql(request, models.CalcRecord, fingerprint, cache_key=cache_key)
        messages.info(request, "Submit raw file completed")
        return self.JsonResponse({})

    def to_project_view(self, request, *args, **kwargs):
        return self.render(request, 'object.html', http_funcs.open_last_object(request))

    def import_blank_file(self, request, *args, **kwargs):
        file = request.FILES.get('blank_file')
        cache_key = request.POST.get('cache_key')
        raw: ap.RawData = pickle.loads(cache.get(cache_key))

        web_file_path, file_name, suffix = ap.files.basic.upload(
            file, settings.UPLOAD_ROOT)
        try:
            with open(web_file_path, 'rb') as f:
                sequences = pickle.load(f)
        except pickle.UnpicklingError:
            return self.JsonResponse({
                'msg': "The file input cannot be unpicked. Please check the file format"},
                encoder=ap.smp.json.MyEncoder, status=403)

        raw.sequence = ap.calc.arr.multi_append(raw.sequence, *sequences)
        http_funcs.create_cache(raw, cache_key=cache_key)

        return self.JsonResponse({'sequences': sequences}, encoder=ap.smp.json.MyEncoder,
                                 content_type='application/json', safe=True)

    def add_empty_blank(self, request, *args, **kwargs):
        raw: ap.RawData = self.sample
        new_blank_sequence = {
            'name': ['EMPTY'],
            'experimentTime': "1996-08-09T08:00:00",
            'Ar36': [[0, 0, 0, 0]],
            'Ar37': [[0, 0, 0, 0]],
            'Ar38': [[0, 0, 0, 0]],
            'Ar39': [[0, 0, 0, 0]],
            'Ar40': [[0, 0, 0, 0]],
        }
        new_sequence = ap.Sequence(
            index='undefined', name=f"empty", data=None, fitting_method=[0, 0, 0, 0, 0],
            datetime=new_blank_sequence['experimentTime'], type_str='blank', is_estimated=True,
            results=[
                new_blank_sequence['Ar36'],
                new_blank_sequence['Ar37'],
                new_blank_sequence['Ar38'],
                new_blank_sequence['Ar39'],
                new_blank_sequence['Ar40'],
            ],
        )

        raw.sequence.append(new_sequence)
        http_funcs.create_cache(raw, cache_key=self.cache_key)  # update raw

        return self.JsonResponse({'new_sequence': new_sequence},
                                 encoder=ap.smp.json.MyEncoder, content_type='application/json', safe=True)

    def change_seq_fitting_method(self, request, *args, **kwargs):
        raw: ap.RawData = self.sample
        seq_idx = self.body['sequence_index']
        iso_idx = self.body['isotope_index']
        fit_idx = self.body['fitting_index']
        # debug_print(f"{seq_idx = }, {iso_idx = }, {fit_idx = }")
        raw.get_sequence(seq_idx).fitting_method[iso_idx] = fit_idx
        http_funcs.create_cache(raw, cache_key=self.cache_key)  # update raw
        return self.JsonResponse({})

    def change_seq_state(self, request, *args, **kwargs):
        raw: ap.RawData = self.sample
        seq_idx = self.body['sequence_index']
        is_blank = self.body['is_blank']
        is_removed = self.body['is_removed']
        seq = raw.get_sequence(seq_idx)
        seq.as_type(is_blank and "blank")
        seq.is_removed = is_removed
        http_funcs.create_cache(raw, cache_key=self.cache_key)  # update raw
        return self.JsonResponse({})

    def calc_raw_chart_clicked(self, request, *args, **kwargs):
        try:
            selectionForAll = self.body['selectionForAll']
            sequence_index = self.body['sequence_index']
            data_index = self.body['data_index']
            isotopic_index = self.body['isotopic_index']
            raw: ap.RawData = self.sample
            for each in data_index:
                status = not raw.sequence[sequence_index].flag[each][isotopic_index * 2 + 1]
                isotopes = list(range(5)) if selectionForAll else [isotopic_index]
                for _isotope in isotopes:
                    raw.sequence[sequence_index].flag[each][_isotope * 2 + 1] = status
                    raw.sequence[sequence_index].flag[each][_isotope * 2 + 2] = status

            raw.do_regression(sequence_index=[sequence_index], isotopic_index=isotopic_index)
        except (BaseException, Exception) as e:
            debug_print(traceback.format_exc())
            self.error_msg = f"{e}"
            messages.error(request, self.error_msg)
            return self.JsonResponse({'msg': self.error_msg}, status=403)
        else:
            http_funcs.create_cache(raw, cache_key=self.cache_key)  # update raw data in cache
            messages.info(request, "Raw data regression completed")
            return self.JsonResponse({'sequence': raw.sequence[sequence_index]},
                                     encoder=ap.smp.json.MyEncoder, content_type='application/json', safe=True)

    def calc_raw_average_blanks(self, request, *args, **kwargs):
        blanks = self.body['blanks']
        newBlank = []
        results = []
        for i in range(5):
            _intercept = sum([j[i]['intercept'] for j in blanks]) / len(blanks)
            _err = ap.calc.err.div(
                (_intercept, ap.calc.err.add(*[j[i]['absolute err'] for j in blanks])), (len(blanks), 0))
            _relative_err = _err / _intercept * 100
            isotope = {
                'isotope': ["Ar36", "Ar37", "Ar38", "Ar39", "Ar40"][i],
                'intercept': _intercept, 'absolute err': _err, 'relative err': _relative_err, 'r2': None, 'mswd': None
            }
            newBlank.append(isotope)
            results.append([[_intercept, _err, _relative_err, np.nan]])
        new_sequence = ap.Sequence(
            index='undefined', name=f"average({', '.join([j[0]['name'] for j in blanks])})", data=None,
            datetime='', type_str='blank', results=results, fitting_method=[0, 0, 0, 0, 0], is_estimated=True,
        )

        raw: ap.RawData = self.sample
        raw.sequence.append(new_sequence)
        http_funcs.create_cache(raw, cache_key=self.cache_key)

        return self.JsonResponse({'newBlank': newBlank, 'new_sequence': new_sequence},
                                 encoder=ap.smp.json.MyEncoder, content_type='application/json', safe=True)

    def calc_raw_interpolated_blanks(self, request, *args, **kwargs):
        """
        Parameters
        ----------
        request
        args
        kwargs

        Returns
        -------

        """

        interpolated_blank = self.body['interpolated_blank']
        raw: ap.RawData = self.sample
        new_sequences = [ap.Sequence(
            name="Interpolated Blank", results=[[[iso[1], 0, np.NaN, np.NaN]] for iso in row],
            fitting_method=[0, 0, 0, 0, 0], index=index, datetime=row[0][0], type_str='blank',
            is_estimated=True,
        ) for index, row in enumerate(interpolated_blank)]
        raw.interpolated_blank = new_sequences

        http_funcs.create_cache(raw, cache_key=self.cache_key)  # update cache

        return self.JsonResponse({'sequences': new_sequences},
                            encoder=ap.smp.json.MyEncoder, content_type='application/json', safe=True)

    def check_regression(self, request, *args, **kwargs):
        raw: ap.RawData = self.sample

        failed = []
        for seq in raw.sequence:
            if seq.is_removed:
                continue
            for ar in range(5):
                regression_res = seq.results[ar][seq.fitting_method[ar]]
                if not all([isinstance(i, (float, int)) for i in regression_res]):
                    failed.append([seq.index, seq.name, f"Ar{36+ar}"])

        msg = "All sequence are valid for later calculation!"
        if failed:
            failed = sorted(list(set([seq[0]+1 for seq in failed])))
            msg = f"Errors: {failed}"
            messages.info(request, f"Check regression completed. Bad regression sequences: {failed}")
        return self.JsonResponse({'status': 'successful', 'msg': msg, 'failed': failed}, status=200)

    def export_sequence(self, request, *args, **kwargs):
        """
        Parameters
        ----------
        request
        args
        kwargs

        Returns
        -------

        """
        raw: ap.RawData = self.sample
        selected = self.body['selected']
        is_blank = self.body['is_blank']
        fitting_method = self.body['fitting_method']

        def _update_sequence(_seq, _is_blank, _fitting_method):
            if _is_blank:
                _seq.type_str = "blank"
            _seq.fitting_method = _fitting_method
            return _seq

        sequences = [_update_sequence(raw.sequence[index], is_blank[index], fitting_method[index])
                     for index, is_selected in enumerate(selected) if is_selected]
        file_path = os.path.join(settings.DOWNLOAD_ROOT,
                                 f"{sequences[0].name}{' et al' if len(sequences) > 1 else ''}.seq")
        export_href = '/' + settings.DOWNLOAD_URL + f"{sequences[0].name}{' et al' if len(sequences) > 1 else ''}.seq"
        with open(file_path, 'wb') as f:  # save serialized json data to a readable text
            f.write(pickle.dumps(sequences))
        messages.info(request, f"Export selected sequences completed")
        return self.JsonResponse({"href": export_href})


class ParamsSettingView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
            "show_irra", "show_calc"
        ]

    def show_irra(self, request, *args, **kwargs):
        names = list(models.IrraParams.objects.values_list('name', flat=True))
        messages.info(request, f'Show parameter project names: {names}')
        return self.render(request, 'irradiation_setting.html', {'allIrraNames': names})

    def show_calc(self, request, *args, **kwargs):
        names = list(models.CalcParams.objects.values_list('name', flat=True))
        messages.info(request, f'Show parameter project names: {names}')
        return self.render(request, 'calculation_setting.html', {'allCalcNames': names})

    def show_smp(self, request, *args, **kwargs):
        names = list(models.SmpParams.objects.values_list('name', flat=True))
        messages.info(request, f'Show parameter project names: {names}')
        return self.render(request, 'sample_setting.html', {'allSmpNames': names})

    def show_input_filter(self, request, *args, **kwargs):
        names = list(models.InputFilterParams.objects.values_list('name', flat=True))
        messages.info(request, f'Show parameter project names: {names}')
        return self.render(request, 'input_filter_setting.html', {'allInputFilterNames': names})

    # def show_export_pdf(self, request, *args, **kwargs):
    #     names = list(models.ExportPDFParams.objects.values_list('name', flat=True))
    #     log_funcs.set_info_log(self.ip, 'info', f'Show export PDF project names: {names}')
    #     return self.render(request, 'export_pdf_setting.html', {'allExportPDFNames': names})

    def change_param_objects(self, request, *args, **kwargs):
        params_type = str(self.body['type'])  # params_type = irra, calc, smp
        name = str(self.body['name'])
        model_name = f"{''.join([i.capitalize() for i in params_type.split('-')])}Params"
        self.write_log(f"Change param objects, {name = }, {params_type = }, {model_name = }")

        try:
            obj = getattr(models, model_name).objects.get(name=name)
        except getattr(models, model_name).DoesNotExist:
            pass
        except (Exception, BaseException) as e:
            messages.error(request, f"{e}")
            return self.JsonResponse({'msg': f"{e}"}, status=403)
        else:
            param = ap.files.basic.read(obj.file_path)
            return self.JsonResponse({'param': param})

        try:
            sample = self.sample
            if name.lower() == "all":
                data = []
                for each_row in sample.TotalParam:
                    data.append("" if len(set(each_row)) != 1 else each_row[0])
            else:
                row = int(name) - 1
                data = ap.calc.arr.transpose(sample.TotalParam)[row]
            if 'irra' in params_type.lower():
                param = [*data[0:20], *data[56:58], *data[20:27],
                         *ap.calc.corr.get_irradiation_datetime_by_string(data[27]), data[28], '', '']
            elif 'calc' in params_type.lower():
                param = [*data[34:56], *data[71:97]]
            elif 'smp' in params_type.lower():
                try:
                    _ = [i == {'l': 0, 'e': 1, 'p': 2}.get(str(data[100]).lower()[0], 0) for i in range(3)]
                except:
                    _ = [True, False, False]
                for i in range(len(data)):
                    if i in range(101, 114) and not isinstance(data[i], bool):
                        data[i] = False
                    elif data[i] is None:
                        data[i] = np.nan
                pref = [sample.Info.preference.get(key, "") for key in ap.smp.initial.preference_keys]
                param = [*data[67:71], *data[58:67], *data[97:100], *data[115:120], *data[126:136],
                         *pref, *_, *data[101:114]]
            elif 'thermo' in params_type.lower():
                # param = [*data[0:20], *data[56:58], *data[20:27],
                #          *ap.calc.corr.get_irradiation_datetime_by_string(data[27]), data[28], '', '']
                pass
            elif 'export' in params_type.lower():
                param = [True]
            else:
                raise KeyError(f"{params_type} is not a supported parameter type")
            param = np.nan_to_num(param).tolist()
        except IndexError as e:
            debug_print(f"{traceback.format_exc()}")
            self.error_msg = f"{e} (1-based). Index = {name}"
            messages.error(request, self.error_msg)
            return self.JsonResponse({'msg': self.error_msg}, status=403)
        except (Exception, BaseException) as e:
            debug_print(f"{traceback.format_exc()}")
            self.error_msg = f"{e}"
            messages.error(request, self.error_msg)
            return self.JsonResponse({'msg': self.error_msg}, status=403)
        else:
            return self.JsonResponse({'param': param})

    def edit_param_object(self, request, *args, **kwargs):
        ip = http_funcs.get_ip(request)
        flag = str(self.body['flag']).lower()
        name = self.body['name']
        pin = self.body['pin']
        params = self.body['params']
        type = str(self.body['type'])  # type = irra, calc, smp, input-filter
        model_name = f"{''.join([i.capitalize() for i in type.split('-')])}Params"
        model = getattr(models, model_name)
        if flag == 'create':
            email = self.body['email']
            if name == '' or pin == '':
                messages.info(request, f'Create parameter project failed, empty name or verification code, name: {name}, code: {pin}')
                return self.JsonResponse({'msg': 'empty name or code'}, status=403)
            elif model.objects.filter(name=name).exists():
                messages.info(request, f'Create parameter project failed, duplicate name, name: {name}')
                return self.JsonResponse({'msg': 'duplicate name'}, status=403)
            else:
                path = ap.files.basic.write(os.path.join(settings.SETTINGS_ROOT, f"{name}.{type}"), params)
                model.objects.create(name=name, pin=pin, file_path=path, uploader_email=email, ip=ip)
                messages.info(request, f'Create parameter project successfully. A {type.lower()} project has been updated, name: {name}, static verification code: {pin}, path: {path}, email: {email}')
                return self.JsonResponse({'status': 'success'})
        else:
            try:
                old = model.objects.get(name=name)
            except (BaseException, Exception):
                debug_print(traceback.format_exc())
                messages.error(request, f'The {type.lower()} project does not exist, name: {name}')
                return self.JsonResponse({'msg': 'current project does not exist'}, status=403)

            # print(f"{old.check_password(pin) = }")
            # if check_password(pin, old.pin):
            if pin == old.pin:
                if flag == 'update':
                    path = ap.files.basic.write(old.file_path, params)
                    old.save()
                    messages.info(request, f'Update parameter project successfully. A {type.lower()} project has been updated, name: {name}, path: {path}')
                    return self.JsonResponse({'status': 'success'})
                elif flag == 'delete':
                    if ap.files.basic.delete(old.file_path):
                        old.delete()
                        messages.info(request, f'Delete parameter project successfully. A {type.lower()} project has been deleted, name: {name}')
                        return self.JsonResponse({'status': 'success'})
                    else:
                        messages.error(request, f'Delete {type.lower()} project failed, name: {name}')
                        return self.JsonResponse({'msg': 'something wrong happened when delete params'}, status=403)
            else:
                self.error_msg = f'Invalid code. Project: {type.lower()}'
                messages.error(request, f"Change or delete parameter project failed. {self.error_msg}, invalid code: {pin}")
                return self.JsonResponse({'msg': self.error_msg}, status=403)

    def set_params(self, request, *args, **kwargs):
        params = list(self.body['params'])
        param_type = str(self.body['type'])  # type = 'irra', or 'calc', or 'smp'
        rows = [i - 1 for i in list(self.body['rows'])]  # zero based
        debug_print(f"{rows = }")
        sample = self.sample
        # backup for later comparision
        components_backup = copy.deepcopy(ap.smp.basic.get_components(sample))

        try:
            sample.set_params(params, param_type, rows)
        except KeyError:
            debug_print(traceback.format_exc())
            messages.error(request, f'Unknown type of params : {param_type}')
            return self.JsonResponse({'msg': f'Unknown type of params : {param_type}'}, status=403)
        except (BaseException, Exception) as e:
            debug_print(traceback.format_exc())
            messages.error(request, f'Set parameters, unknown error: {type(e).__name__}: {str(e)}')
            return self.JsonResponse({'msg': f'{type(e).__name__}: {str(e)}'}, status=403)

        ap.smp.table.update_table_data(sample)  # Update data of tables after changes of calculation parameters
        # update cache
        http_funcs.create_cache(sample, self.cache_key)
        res = ap.smp.basic.get_diff_smp(backup=components_backup, smp=ap.smp.basic.get_components(sample))
        # debug_print(f"Diff after reset_calc_params: {res}")
        messages.error(request, f'Set parameters completed')
        return self.JsonResponse({'msg': 'Successfully!', 'changed_components': ap.smp.json.dumps(res)}, status=200)


class ThermoView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = []

    # /calc/thermo
    def get(self, request, *args, **kwargs):
        # names = list(models.IrraParams.objects.values_list('name', flat=True))
        # log_funcs.set_info_log(self.ip, 'info', f'Show irradiation param project names: {names}')
        allThermoNames = list(models.ThermoParams.objects.values_list('name', flat=True))
        return self.render(request, 'thermo.html', {'allThermoNames': allThermoNames})

    # /calc/thermo/arr_input
    def arr_input(self, request, *args, **kwargs):
        random_index = request.POST.get('random_index')
        arr_file = request.POST.get('arr_file_name')
        heating_log_file = request.POST.get('heating_log_file_name')
        smp_name = request.POST.get('sample_name')
        suffix = ''
        destination_folder, random_index = ap.smp.diffusion_funcs.get_random_dir(
            settings.MDD_ROOT, length=7, random_index=random_index)
        for i in range(len(request.FILES)):
            try:
                file = request.FILES.get(str(i))
                web_file_path, file_name, suffix = ap.files.basic.upload(file, destination_folder)
            except (Exception, BaseException) as e:
                pass
            else:
                if str(suffix).lower() == ".arr":
                    arr_file = file_name + suffix
                    sample = ap.from_arr(file_path=web_file_path)
                    smp_name = sample.name()
                elif suffix != "":
                    heating_log_file = file_name + suffix

        return self.JsonResponse({"sample_name": smp_name, "arr_file": arr_file, "heating_log_file": heating_log_file,
                             "random_index": random_index, "suffix": suffix})

    # /calc/thermo/check_sample
    def check_sample(self, request, *args, **kwargs):
        # names = list(models.IrraParams.objects.values_list('name', flat=True))
        # log_funcs.set_info_log(self.ip, 'info', f'Show irradiation param project names: {names}')

        name = self.body['name']
        arr_file_name = self.body['arr_file_name']
        random_index = self.body['random_index']
        params = self.body['settings']

        use_ln = True if str(params[6]).lower() == 'ln' else False
        logdr2_method = params[7]  # xlogd (logr/r0) method
        argon = params[10]

        loc = os.path.join(settings.MDD_ROOT, f'{random_index}')
        if not os.path.exists(loc) or random_index == "":
            return self.JsonResponse({}, status=403)

        if arr_file_name == "":
            for root, dirs, files in os.walk(loc):
                for file in files:
                    if file.endswith('.arr'):
                        arr_file_name = file
                        name = arr_file_name.strip('.arr')

        mch_out = os.path.join(loc, f'{arr_file_name}_mch-out.dat')
        mages_out = os.path.join(loc, f'{arr_file_name}_mages-out.dat')
        ages_sd = os.path.join(loc, f'{arr_file_name}_ages-sd.samp')
        file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))

        sample = ap.from_arr(file_path=file_path)
        sequence = sample.sequence()
        nsteps = sequence.size
        te = np.array(sample.TotalParam[124], dtype=np.float64)
        ti = (np.array(sample.TotalParam[123], dtype=np.float64) / 60).round(2)  # time in minute
        nindex = {"40": 24, "39": 20, "38": 10, "37": 8, "36": 0}
        if argon in list(nindex.keys()):
            ar = np.array(sample.DegasValues[nindex[argon]], dtype=np.float64)  # 20-21 Argon
            sar = np.array(sample.DegasValues[nindex[argon] + 1], dtype=np.float64)
        elif argon == 'total':
            all_ar = np.array(sample.CorrectedValues, dtype=np.float64)  # 20-21 Argon
            ar, sar = ap.calc.arr.add(*all_ar.reshape(5, 2, len(all_ar[0])))
            ar = np.array(ar); sar = np.array(sar)
        else:
            raise KeyError
        age = np.array(sample.ApparentAgeValues[2], dtype=np.float64)  # 2-3 age
        sage = np.array(sample.ApparentAgeValues[3], dtype=np.float64)
        f = np.cumsum(ar) / ar.sum()

        # dr2, ln_dr2 = ap.smp.diffusion_funcs.dr2_popov(f, ti)
        try:
            if str(logdr2_method).lower().startswith('plane'.lower()):
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_plane(f, ti, ar=ar, sar=sar, ln=use_ln)
            elif str(logdr2_method).lower() == 'yang':
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_yang(f, ti, ar=ar, sar=sar, ln=use_ln)
            elif str(logdr2_method).lower().startswith('sphere'.lower()):
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_sphere(f, ti, ar=ar, sar=sar, ln=use_ln)
            elif str(logdr2_method).lower().startswith('Thern'.lower()):
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_thern(f, ti, ar=ar, sar=sar, ln=use_ln)
            else:
                raise KeyError(f"Geometric model not found: {str(logdr2_method).lower()}")
        except (Exception, BaseException) as e:
            return self.JsonResponse({'msg': f"The D/r2 calculation failed. {type(e).__name__}: {str(e)}"}, status=403)

        data = np.array([
            sequence.value, te, ti, age, sage, ar, sar, f, dr2, ln_dr2, wt
        ]).tolist()
        data.insert(0, (np.where(np.array(data[3]) > 0, True, False) & np.isfinite(data[3])).tolist())
        data.insert(1, [1 for i in range(nsteps)])

        res = False
        if os.path.isfile(mch_out) and os.path.isfile(mages_out) and os.path.isfile(ages_sd):
            res = True

        return self.JsonResponse({'status': 'success', 'has_files': res, 'data': ap.smp.json.dumps(data),
                             'name': name, 'arr_file_name': arr_file_name})


    def run_arrmulti(self, request, *args, **kwargs):
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        random_index = self.body['random_index']
        max_age = self.body['max_age']
        data = self.body['data']
        params = self.body['settings']

        debug_print(data)
        debug_print(params)

        loc = os.path.join(settings.MDD_ROOT, f'{random_index}')
        if not os.path.exists(loc) or random_index == "":
            return self.JsonResponse({"random_index": random_index}, status=403)

        file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
        sample = ap.from_arr(file_path=file_path)

        arr = ap.smp.diffusion_funcs.DiffArrmultiFunc(smp=sample, loc=loc)

        filtered_data = list(filter(lambda x: x[0], data))
        filtered_index = [i for i, row in enumerate(data) if row[0]]
        arr.ni = len(filtered_data)
        data = ap.calc.arr.transpose(data)
        filtered_data = ap.calc.arr.transpose(filtered_data)
        arr.telab = [i + 273.15 for i in filtered_data[3]]
        arr.tilab = [i * 60 for i in filtered_data[4]]
        arr.ya = filtered_data[5]
        arr.sig = filtered_data[6]
        arr.a39 = filtered_data[7]
        arr.sig39 = filtered_data[8]
        arr.f = filtered_data[9]
        # dr2, arr.xlogd, arr.wt = ap.smp.diffusion_funcs.dr2_lovera(
        #     f=arr.f, ti=filtered_data[4], ar=filtered_data[7], sar=filtered_data[8], ln=False)
        dr2, arr.xlogd, arr.wt = filtered_data[10:13]

        arr.f.insert(0, 0)
        arr.f = np.where(np.array(arr.f) >= 1, 0.9999999999999999, np.array(arr.f))
        arr.main()

        return self.JsonResponse({})


    def run_agemon(self, request, *args, **kwargs):
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        random_index = self.body['random_index']
        max_age = self.body['max_age']
        data = self.body['data']
        loc = os.path.join(settings.MDD_ROOT, random_index)
        if not os.path.exists(loc) or random_index == "":
            return self.JsonResponse({}, status=403)

        file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
        sample = ap.from_arr(file_path=file_path)

        sample.name(arr_file_name)

        use_dll = True
        # use_dll = False

        data = list(filter(lambda x: x[0], data))

        if use_dll:
            if os.name == 'nt':  # Windows system
                source = os.path.join(settings.SETTINGS_ROOT, "mddfuncs.dll")
            elif os.name == 'posix':  # Linux
                source = os.path.join(settings.SETTINGS_ROOT, "mddfuncs.so")
            else:
                return self.JsonResponse({}, status=403)
            ap.smp.diffusion_funcs.run_agemon_dll(sample, source, loc, data, float(max_age))
        else:
            agemon = ap.smp.diffusion_funcs.DiffAgemonFuncs(smp=sample, loc=loc)

            agemon.max_plateau_age = float(max_age)
            agemon.ni = len(data)
            agemon.nit = agemon.ni
            data = ap.calc.arr.transpose(data)
            agemon.r39 = np.zeros(agemon.nit + 1, dtype=np.float64)
            agemon.telab = np.zeros(100, dtype=np.float64)
            agemon.tilab = np.zeros(100, dtype=np.float64)
            agemon.ya = np.zeros(100, dtype=np.float64)
            agemon.sig = np.zeros(100, dtype=np.float64)
            agemon.a39 = np.zeros(100, dtype=np.float64)
            agemon.sig39 = np.zeros(100, dtype=np.float64)
            agemon.xs = np.zeros(100, dtype=np.float64)

            for i in range(agemon.nit):
                agemon.ya[i + 1] = data[5][i]
                agemon.sig[i] = data[6][i]
                agemon.a39[i] = data[7][i]
                agemon.sig39[i] = data[8][i]
                agemon.xs[i + 1] = data[9][i]
                agemon.telab[i] = data[3][i] + 273.15
                agemon.tilab[i] = data[4][i] / 5.256E+11

            agemon.xs = np.where(np.array(agemon.xs) >= 1, 0.9999999999999999, np.array(agemon.xs))

            for i in range(agemon.nit):
                if agemon.telab[i] > 1373:
                    agemon.ni = i
                    break

            agemon.main()



        return self.JsonResponse({})


    def run_walker(self, request, *args, **kwargs):
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        random_index = self.body['random_index']
        max_age = self.body['max_age']
        data = self.body['data']
        params = self.body['settings']

        if params[10] == "40":
            return self.run_40ar_walker(request, args, kwargs)

        loc = os.path.join(settings.MDD_ROOT, f'{random_index}')
        if not os.path.exists(loc) or random_index == "":
            return self.JsonResponse({"random_index": random_index}, status=403)
        arr_file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))

        # setting_params = params[:11]
        domain_params = params[11:33]
        # tc_params = params[33:36]
        checkable_params = params[-10:]

        # 活化能和体积比例从外到内
        energies = (np.array(domain_params[0:16:2]) * 1000).tolist()
        fractions = domain_params[1:16:2]
        ndoms = list(energies).index(0)
        use_walker1 = domain_params[16] == "walker1"
        k = domain_params[17]
        gs = domain_params[18]
        ad = domain_params[19]  # atom density
        f = domain_params[20]  # frequency
        pumping = domain_params[21]
        # ad = 1e10  # atom density
        # f = 1e13
        dimension = 3

        debug_print(f"{use_walker1 = }, {k = }, {gs = }, {ad = }, {f = }")

        smp = ap.from_arr(arr_file_path)
        ti = np.array(smp.TotalParam[123], dtype=np.float64).round(2)  # time in second
        temps = np.array(smp.TotalParam[124], dtype=np.float64)  # temperature in Celsius
        ar = np.array(smp.DegasValues[20], dtype=np.float64)  # Ar39K
        targets = ar.cumsum() / sum(ar)

        statuses = [True for i in range(len(ti))]

        if checkable_params[6]:  # including pumping phases
            for i in range(0, len(ti) * 2, 2):
                if checkable_params[7]:  # pumping out after, like Y56
                    ti = np.insert(ti, i+1, pumping)
                    if checkable_params[8]:  # heating durations include pumping-out phases
                        ti[i] -= pumping
                else:
                    ti = np.insert(ti, i, pumping)
                    # times = np.insert(times, i, times[i] - pumping)
                    if checkable_params[8]:  # heating durations include pumping-out phases
                        ti[i+1] -= pumping
                temps = np.insert(temps, i+1, temps[i])
                targets = np.insert(targets, i+1, targets[i])
                statuses.insert(i+1, False)

        times = np.cumsum(ti)  # cumulative time

        debug_print(list(zip(temps, times)))

        if checkable_params[9]:  # searching for nearby places
            energies_list = []; fractions_list = []
            for each in energies[: ndoms]:
                energies_list.append([each + i * 1000 for i in range(-1, 2, 1)])
            for each in fractions[: ndoms]:
                fractions_list.append([each + i * 0.01 if each != 1 else 1 for i in range(-1, 2, 1)])
            e_combinations = list(itertools.product(*energies_list))
            f_combinations = list(itertools.product(*fractions_list))
        else:
            e_combinations = [energies[: ndoms]]
            f_combinations = [fractions[: ndoms]]

        for index, (_e, _f) in enumerate(list(itertools.product(*[e_combinations, f_combinations]))):
            debug_print(f"{index = }, {_e = }, {_f = }")

            file_name = f"{'walker1' if use_walker1 else 'walker2'} {k=:.1f} " \
                        f"es={'-'.join([str(int(i / 1000)) for i in _e])} " \
                        f"fs={'-'.join([str(i) for i in _f])} " \
                        f"{gs=:.0f} " \
                        f"{ad=:.0e} " \
                        f"{f=:.0e} " \
                        f"{ndoms=:.0f} " \
                        f"pumping={checkable_params[6]} " \
                        f"multi"

            try:
                _start = time.time()
                demo, status = ap.thermo.arw.run(
                    times, temps, statuses,
                    _e, _f, ndoms, file_name=file_name, k=k, grain_szie=gs, dimension=dimension,
                    atom_density=ad, frequency=f, simulation=False, targets=targets, epsilon=0.05, use_walker1=use_walker1
                )
            except ap.thermo.arw.OverEpsilonError as e:
                debug_print(traceback.format_exc())
                return self.JsonResponse({})
            else:
                debug_print(traceback.format_exc())
                ap.thermo.arw.save_ads(demo, f"{loc}", name=demo.name + f" {(time.time() - _start) / 3600:.2f}h")

        return self.JsonResponse({})


    def run_40ar_walker(self, request, *args, **kwargs):
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        random_index = self.body['random_index']
        max_age = self.body['max_age']
        data = self.body['data']
        params = self.body['settings']
        loc = os.path.join(settings.MDD_ROOT, f'{random_index}')
        if not os.path.exists(loc) or random_index == "":
            return self.JsonResponse({"random_index": random_index}, status=403)
        arr_file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))

        # setting_params = params[:11]
        domain_params = params[11:33]
        # tc_params = params[33:36]
        checkable_params = params[-10:]

        # 活化能和体积比例从外到内
        energies = (np.array(domain_params[0:16:2]) * 1000).tolist()
        fractions = domain_params[1:16:2]
        ndoms = list(energies).index(0)
        use_walker1 = domain_params[16] == "walker1"
        k = domain_params[17]
        gs = domain_params[18]
        ad = domain_params[19]  # atom density
        ad = 0  # atom density
        parent = domain_params[19]  # parent 40K
        f = domain_params[20]  # frequency
        pumping = domain_params[21]
        # ad = 1e10  # atom density
        # f = 1e13
        dimension = 3

        debug_print(f"Run 40Ar {use_walker1 = }, {k = }, {gs = }, {ad = }, {f = }")

        smp = ap.from_arr(arr_file_path)

        age = 20  # 20 Ma
        scale = 100000  # 0.1 Ma
        dt = 3600 * 24 * 365.2425 * scale  # 0.1 Ma
        ti = np.ones(int(age * 1000000 / scale)) * dt
        temps = np.ones(int(age * 1000000 / scale)) * 10
        temps[:5] = 400
        temps[5:10] = 400
        temps[10:20] = 350
        temps[20:30] = 300
        temps[30:40] = 250
        temps[40:50] = 200
        temps[50:70] = 150
        temps[70:100] = 25
        temps[100:] = 10

        times = np.cumsum(ti)  # cumulative time
        statuses = [True for i in range(len(ti))]
        targets = [0 for i in range(len(ti))]
        debug_print(list(zip(temps, times)))

        e_combinations = [energies[: ndoms]]
        f_combinations = [fractions[: ndoms]]

        for index, (_e, _f) in enumerate(list(itertools.product(*[e_combinations, f_combinations]))):
            debug_print(f"{index = }, {_e = }, {_f = }")

            ## 先模拟热史

            file_name = f"{'walker1' if use_walker1 else 'walker2'} {k=:.1f}a " \
                        f"es={'-'.join([str(int(i / 1000)) for i in _e])} " \
                        f"fs={'-'.join([str(i) for i in _f])} " \
                        f"{dt=:.0f} " \
                        f"{parent=:.0f} " \
                        f"{gs=:.0f} " \
                        f"{ad=:.0e} " \
                        f"{f=:.0e} " \
                        f"{ndoms=:.0f} " \
                        f"temp={set(temps)} " \
                        f"pumping={checkable_params[6]} " \
                        f"multi"

            try:
                _start = time.time()
                k = 3600 * 24 * 365.2425 * k
                # demo, status = ap.thermo.main.run(
                #     times, temps, statuses,
                #     _e, _f, ndoms, file_name=file_name, k=k, grain_szie=gs, dimension=dimension,
                #     atom_density=ad, frequency=f, simulation=False, targets=targets, epsilon=0.05,
                #     use_walker1=use_walker1, decay=5.53e-10, parent=parent
                # )
            except ap.thermo.arw.OverEpsilonError as e:
                debug_print(traceback.format_exc())
                return self.JsonResponse({})
            else:
                debug_print(traceback.format_exc())
                # ap.thermo.main.save_ads(demo, f"{loc}", name=demo.name + f" {(time.time() - _start) / 3600:.2f}h")

                filename = f"walker2 k=10000.0a es=135-126-152 fs=1-0.97-0.74 dt=3155695200000 parent=800000000 gs=275 ad=0e+00 f=1e+13 ndoms=3 pumping=True multi 1.35h.ads"
                filename = "walker2 k=3000.0a es=135-126-152 fs=1-0.97-0.74 dt=3155695200000 parent=800000000 gs=275 ad=0e+00 f=1e+13 ndoms=3 temp={200.0, 10.0, 300.0, 400.0, 150.0, 25.0, 250.0, 350.0} pumping=True multi 4.99h.ads"
                filename = "walker2 k=1000.0a es=135-126-152 fs=1-0.97-0.74 dt=3155695200000 parent=800000000 gs=275 ad=0e+00 f=1e+13 ndoms=3 pumping=False multi 12.27h.ads"
                filename = os.path.join(r"D:\DjangoProjects\webarar\private\mdd\20240920_24FY88a\thermo-history", filename)
                demo = ap.thermo.arw.read_ads(filename)


                ## 再模拟实验过程

                use_walker1 = False
                k = 10

                file_name = f"{'walker1' if use_walker1 else 'walker2'} {k=:.1f}a " \
                            f"es={'-'.join([str(int(i / 1000)) for i in _e])} " \
                            f"fs={'-'.join([str(i) for i in _f])} " \
                            f"{dt=:.0f} " \
                            f"{gs=:.0f} " \
                            f"{ad=:.0e} " \
                            f"{f=:.0e} " \
                            f"{ndoms=:.0f} " \
                            f"pumping={checkable_params[6]} " \
                            f"multi"

                ti = np.array(smp.TotalParam[123], dtype=np.float64).round(2)  # time in second
                temps = np.array(smp.TotalParam[124], dtype=np.float64)  # temperature in Celsius
                ar = np.array(smp.DegasValues[24], dtype=np.float64)  # Ar40r
                targets = ar.cumsum() / sum(ar)
                statuses = [True for i in range(len(ti))]

                if checkable_params[6]:  # including pumping phases
                    for i in range(0, len(ti) * 2, 2):
                        if checkable_params[7]:  # pumping out after, like Y56
                            ti = np.insert(ti, i + 1, pumping)
                            if checkable_params[8]:  # heating durations include pumping-out phases
                                ti[i] -= pumping
                        else:
                            ti = np.insert(ti, i, pumping)
                            # times = np.insert(times, i, times[i] - pumping)
                            if checkable_params[8]:  # heating durations include pumping-out phases
                                ti[i + 1] -= pumping
                        temps = np.insert(temps, i + 1, temps[i])
                        targets = np.insert(targets, i + 1, targets[i])
                        statuses.insert(i + 1, False)

                times = np.cumsum(ti)  # cumulative time

                debug_print(list(zip(temps, times)))

                try:
                    _start = time.time()
                    k = 3600 * 24 * 365.2425 * k
                    demo, status = ap.thermo.arw.run(
                        times, temps, statuses, _e, _f, ndoms, file_name=file_name, k=k, grain_szie=gs, dimension=dimension,
                        atom_density=ad, frequency=f, simulation=False, targets=targets, epsilon=0.05,
                        use_walker1=use_walker1, decay=0, parent=0, positions=demo.positions
                    )
                except ap.thermo.arw.OverEpsilonError as e:
                    debug_print(traceback.format_exc())
                    return self.JsonResponse({})
                else:
                    debug_print(traceback.format_exc())
                    ap.thermo.arw.save_ads(demo, f"{loc}", name=demo.name + f" {(time.time() - _start) / 3600:.2f}h")

        return self.JsonResponse({})


    def plot(self, request, *args, **kwargs):
        # names = list(models.IrraParams.objects.values_list('name', flat=True))
        # log_funcs.set_info_log(self.ip, 'info', f'Show irradiation param project names: {names}')
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        heating_log = self.body['heating_log_file_name']
        random_index = self.body['random_index']
        data = self.body['data']
        params = self.body['settings']

        loc = os.path.join(settings.MDD_ROOT, f'{random_index}')
        if not os.path.exists(loc) or random_index == "":
            return self.JsonResponse({}, status=403)

        n = len(data)
        data = ap.calc.arr.transpose(data)

        # read_from_ins = True
        read_from_ins = False

        use_ln = True if str(params[6]).lower() == 'ln' else False
        logdr2_method = params[7]  # xlogd (logr/r0) method
        tc_params = [A, cooling_rate, radius] = params[33:36]
        temp_err = 5
        plot_params = params[37:42]
        base = np.e if use_ln else 10

        groups = set(data[1])
        lines = []
        if plot_params[0]:  # arrhenius plot
            for each_group in groups:
                each_line = [np.nan for i in range(17)]  # [b, sb, a, sa, ..., energy, se, tc, stc]
                ti = [i + 273.15 for i in data[3]]
                x, y, wtx, wty = [], [], [], []
                for i in range(len(ti)):
                    if str(data[1][i]) == str(each_group) and data[0][i]:
                        x.append(10000 / ti[i])
                        wtx.append(10000 * temp_err / ti[i] ** 2)
                        y.append(data[11][i])
                        wty.append(data[12][i])
                if len(x) > 0:

                    @np.vectorize
                    def get_da2_e_Tc(b, m):
                        k1 = base ** b * ap.thermo.basic.SEC2YEAR  # k1: da2
                        if str(logdr2_method).lower().startswith('Thern'.lower()):
                            k1 = k1 / (radius * 0.0001) ** 2  # μm to m
                        # Closure temperature
                        k2 = -10 * m * ap.thermo.basic.GAS_CONSTANT * np.log(base)  # activation energy, kJ
                        k3, _ = ap.thermo.basic.get_tc(da2=k1, sda2=0, E=k2 * 1000, sE=0, pho=0, cooling_rate=cooling_rate, A=A)
                        return k1, k2, k3  # da2, E, Tc

                    try:
                        # Arrhenius line regression
                        # each_line[0:6] = ap.thermo.basic.fit(x, y, wtx, wty)  # intercept, slop, sa, sb, chi2, q
                        # b (intercept), sb, a (slope), sa, mswd, dF, Di, k, r2, chi_square, p_value, avg_err_s, cov
                        each_line[0:13] = ap.calc.regression.york2(x, wtx, y, wty, ri=np.zeros(len(x)))
                        each_line[1] = each_line[1] * 2  # 2 sigma
                        each_line[3] = each_line[3] * 2  # 2 sigma

                        # monte carlo simulation with 4000 trials
                        cov_matrix = np.array([[each_line[1] ** 2, each_line[12]], [each_line[12], each_line[3] ** 2]])
                        mean_vector = np.array([each_line[0], each_line[2]])
                        random_numbers = np.random.multivariate_normal(mean_vector, cov_matrix, 4000)
                        res, cov = ap.calc.basic.monte_carlo(get_da2_e_Tc, random_numbers, confidence_level=0.95)
                        da2, E, Tc = res[0:3, 0]
                        # sda2, sE, sTc = np.diff(res[0:3, [1, 2]], axis=1).flatten() / 2
                        sda2, sE, sTc = 2 * cov[0, 0] ** .5, 2 * cov[1, 1] ** .5, 2 * cov[2, 2] ** .5  # 95%

                        each_line[13:15] = [E, sE]
                        each_line[15:17] = [Tc, sTc]

                    except:
                        debug_print(traceback.format_exc())
                        pass
                lines.append(each_line)

        spectra_data = [[], [], [], []]
        wtd_mean_ages = []
        if plot_params[1]:  # Age spectra
            spectra_data[0] = ap.calc.spectra.get_data(data[5], data[6], [i * 100 for i in data[9]], cumulative=True)
            for each_group in groups:
                age, sage, indexes = [], [], []
                for i in range(len(data[1])):
                    if str(data[1][i]) == str(each_group) and data[0][i]:
                        age.append(data[5][i])
                        sage.append(data[6][i])
                        indexes.append(i)
                wtd_mean_ages.append([data[9][min(indexes) - 1] * 100 if min(indexes) != 0 else 0, data[9][max(indexes)] * 100, *ap.calc.arr.wtd_mean(age, sage)])

        if plot_params[2]:  # cooling history
            if read_from_ins:
                mdd_loc = r"C:\Users\Young\OneDrive\00-Projects\【2】个人项目\2024-06 MDD\MDDprograms\Sources Codes"
                arr = ap.smp.diffusion_funcs.DiffDraw(name="Y51a", loc=mdd_loc, read_from_ins=read_from_ins)
            else:
                file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
                sample = ap.from_arr(file_path=file_path)

                arr = ap.smp.diffusion_funcs.DiffDraw(smp=sample, loc=loc)
                arr.ni = n
                arr.telab = [i + 273.15 for i in data[3]]
                arr.tilab = [i * 60 for i in data[4]]
                arr.age = data[5]
                arr.sage = data[6]
                arr.a39 = data[7]
                arr.sig39 = data[8]
                arr.f = data[9]
            spectra_data[1:] = list(arr.get_plot_data())[1:]
        else:
            spectra_data[1:] = [[], [], []]

        furnace_log = []
        heating_out = []
        if plot_params[3]:  # heating log
            try:
                furnace_log = libano_log = np.loadtxt(os.path.join(loc, f"{heating_log}"), delimiter=',')
                # heating_out = np.loadtxt(os.path.join(loc, f"{file_name}-heated-index.txt"), delimiter=',', dtype=int)
                # heating_out = np.loadtxt(os.path.join(loc, f"{file_name}-heated-index.txt"), delimiter=',', dtype=int)
            except FileNotFoundError:
                debug_print(f"FileNotFoundError")
                furnace_log = [[], [], [], [], [], []]
                heating_out = []
            else:
                # passs
                # heating_timestamp = [j for v in heating_out for j in libano_log[0, v]]  # 加热起止点的时间标签
                # furnace_log = [libano_log[:, 0]]
                # for i in range(1, libano_log.shape[1] - 1):
                #     if not all([(i==i[0]).all() for i in libano_log[[1, 2, 4, 5], i-1: i+2]]) or libano_log[0, i] in heating_timestamp:
                #         furnace_log.append(libano_log[:, i])
                # furnace_log.append(libano_log[:, -1])
                # furnace_log = np.transpose(furnace_log)
                # heating_out = np.reshape([index for index, _ in enumerate(furnace_log[0]) if _ in heating_timestamp], (len(heating_timestamp) // 2, 2))
                pass
        spectra_data.append(furnace_log)
        spectra_data.append(heating_out)

        released = []
        release_name = []
        if plot_params[4]:  # release pattern
            ar = data[7]
            ads_released = []
            index = 1
            for (dirpath, dirnames, fs) in os.walk(loc):
                for f in fs:
                    if f.endswith(".ads"):
                        if not os.path.exists(os.path.join(loc, f)):
                            continue
                        index += 1
                        release_name.append(f"Released{index}: {f}")
                        diff = ap.thermo.arw.read_ads(os.path.join(loc, f))
                        debug_print(f"{f = }, {len(diff.released_per_step) = }, {diff.atom_density = :.0e}")
                        ads_released.append(np.array(diff.released_per_step) / diff.natoms)

            ads_released = np.transpose(ads_released)

            for i in range(len(ads_released)):
                released.append([i+1, sum(ar[0:i+1]) / sum(ar), *ads_released[i]])
        else:
            released.append([])
        spectra_data.append(released)
        release_name = '\n'.join(release_name)

        return self.JsonResponse({'status': 'success', 'data': ap.smp.json.dumps(spectra_data),
                             'line_data': ap.smp.json.dumps(lines),
                             'wtd_mean_ages': ap.smp.json.dumps(wtd_mean_ages),
                             'release_name': release_name})


    def read_log(self, request, *args, **kwargs):
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        loc = f"C:\\Users\\Young\\OneDrive\\00-Projects\\【2】个人项目\\2022-05论文课题\\【3】分析测试\\ArAr\\01-VU实验数据和记录\\{sample_name}"

        libano_log_path = f"{loc}\\Libano-log"
        libano_log_path = [os.path.join(libano_log_path, i) for i in os.listdir(libano_log_path)]
        helix_log_path = f"{loc}\\LogFiles"
        helix_log_path = [os.path.join(helix_log_path, i) for i in os.listdir(helix_log_path)]

        ap.smp.diffusion_funcs.SmpTemperatureCalibration(
            libano_log_path=libano_log_path, helix_log_path=helix_log_path, loc=loc, name=arr_file_name)

        return self.JsonResponse({})


class ExportView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = []

    # /calc/export
    def get(self, request, *args, **kwargs):
        names = list(models.ExportPdfParams.objects.values_list('name', flat=True))
        return self.render(request, 'export_pdf_setting.html', {'allExportPDFNames': names})

    def get_plotdata(self, request, *args, **kwargs):
        page_settings = self.body['settings']
        freshing = self.body['fresh']
        preview = self.body['preview']
        data = self.body['data']
        files_table = json.loads(self.body['json_string'])['files']
        files_table = list(filter(lambda row: row['checked'], files_table))
        for index, row in enumerate(files_table):
            row.update({'rank': int(row['position'])})
            if int(row['position']) == 0 and index != 0:
                row['rank'] = int(files_table[index-1]['rank']) + 1
        files_table = sorted(files_table, key=lambda row: int(row['rank']))

        debug_print(files_table)

        colors = [
            '#1f3c40', '#e35000', '#e1ae0f', '#3d8ebf', '#77dd83', '#c7ae88', '#83d6bb', '#653013', '#cc5f16',
            '#d0b269',
            '#002b5b', '#d7263d', '#3a9679', '#f49d1a', '#523e6a', '#97a7b3', '#ff6f61', '#2a9d8f', '#e63946',
            '#264653',
            '#ffe156', '#6a0572', '#e6399b', '#255f85', '#47e5bc', '#ff924c', '#1b1f3b', '#d7c9aa', '#935116', '#495867'
        ]

        def get_smp(file_path):
            _, ext = os.path.splitext(file_path)
            if ext[1:] not in ['arr', 'age']:
                raise ValueError(f"Cannot open file: {file_path}")
            return (ap.from_arr if ext[1:] == 'arr' else ap.from_age)(file_path)

        keys = [
            "page_size", "ppi", "width", "height", "pt_width", "pt_height", "pt_left", "pt_bottom",
            "offset_top", "offset_right", "offset_bottom", "offset_left", "num_columns", "show_label",
            "show_frame",
        ]
        page_settings = dict(zip(keys, [int(val) if str(val).isnumeric() else val for val in page_settings]))

        data = {
            "data": [],
            "file_name": "WebArAr"
        } if data == {} else data

        # ------ 构建数据 -------
        page_num = -1; c = 0; plot_data_list = []; params_list = []
        for index, row in enumerate(files_table):
            params_list.append(dict(zip(keys, [int(val) if str(val).isnumeric() else val for val in ap.files.basic.read(models.ExportPdfParams.objects.get(name=row['setting']).file_path)])))
            if index == 0 or int(row['position']) == 1:
                page_num += 1; c = 0; plot_data_list.append([]); xn = 0; yn = 0; sn = 0
            plot_together = int(row['position']) == 0
            plot_data = ap.smp.export.get_plot_data(smp=get_smp(row['file_path']), diagram=row['diagram'], color=colors[c] if plot_together else 'black')
            if freshing:  # freshing: 获取 前端 axis属性，更新series
                plot_data['xAxis'] = data['data'][page_num]['xAxis'][xn:xn+len(plot_data['xAxis'])]
                plot_data['yAxis'] = data['data'][page_num]['yAxis'][yn:yn+len(plot_data['yAxis'])]
                xn = xn + len(plot_data['xAxis']); yn = yn + len(plot_data['yAxis'])
                if preview:  # preview: 完全从前端读取 点击 fresh的时候 fresh == True and preview == False  点击 preview 的时候 fresh == True and preview == True
                    plot_data['series'] = data['data'][page_num]['series'][sn:sn+len(plot_data['series'])]
                    sn = sn + len(plot_data['series'])
                else:
                    plot_data['series'] = ap.smp.export.get_plot_series_data(smp=get_smp(row['file_path']), diagram=row['diagram'], color=colors[c] if plot_together else 'black', xAxis=plot_data['xAxis'], yAxis=plot_data['yAxis'])
            if plot_together:
                plot_data_list[-1][-1]['series'].extend(plot_data['series'])
            else:
                plot_data_list[-1].append(plot_data)
            c += 1

        data['data'] = []
        for page in plot_data_list:
            data['data'].append({'name': "", 'xAxis': [], 'yAxis': [], 'series': []})
            for cv in page:
                data['data'][-1]['xAxis'].extend(cv['xAxis'])
                data['data'][-1]['yAxis'].extend(cv['yAxis'])
                data['data'][-1]['series'].extend(cv['series'])
        params_list = iter(params_list)
        cvs = [[ap.smp.export.get_cv_from_dict(plot, **next(params_list)) for plot in page] for page in plot_data_list]

        file_path = f"{settings.DOWNLOAD_URL}{data['file_name']}-{uuid.uuid4().hex[:8]}.pdf"
        try:
            file_path = ap.smp.export.export_chart_to_pdf(cvs, file_name=data['file_name'], file_path=file_path, **page_settings)
        except (Exception, BaseException) as e:
            messages.error(request, e)
            return self.JsonResponse({'msg': f"{e}"}, status=403)
        else:
            export_href = '/' + file_path
            messages.info(request, f"Export to DPF completed. {file_path = }.")
            return self.JsonResponse({'data': ap.smp.json.dumps(data), 'href': export_href})


class ApiView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
        ]

    @staticmethod
    def open_raw(request, *args, **kwargs):
        return CalcHtmlView().open_raw_file(request, *args, **kwargs)

    @staticmethod
    def open_arr(request, *args, **kwargs):
        return CalcHtmlView().open_arr_file(request, *args, **kwargs)

    @staticmethod
    def open_full(request, *args, **kwargs):
        return CalcHtmlView().open_full_xls_file(request, *args, **kwargs)

    @staticmethod
    def open_age(request, *args, **kwargs):
        return CalcHtmlView().open_age_file(request, *args, **kwargs)

    @staticmethod
    def open_current(request, *args, **kwargs):
        return CalcHtmlView().open_current_file(request, *args, **kwargs)

    @staticmethod
    def open_new(request, *args, **kwargs):
        return CalcHtmlView().open_new_file(request, *args, **kwargs)

    @staticmethod
    def open_multi(request, *args, **kwargs):
        return CalcHtmlView().open_multi_files(request, *args, **kwargs)

    def multi_files(self, request, *args, **kwargs):
        res = []
        try:
            length = int(request.POST.get('length'))
        except TypeError:
            files = request.FILES.getlist('files')
        else:
            files = [request.FILES.get(str(i)) for i in range(length)]
        debug_print(f"Number of files: {len(files)}")
        for file in files:
            try:
                web_file_path, file_name, suffix = ap.files.basic.upload(
                    file, settings.UPLOAD_ROOT)
            except (Exception, BaseException):
                continue
            else:
                res.append({
                    'name': file_name, 'extension': suffix, 'path': web_file_path,
                })
        return self.JsonResponse({'files': res})

    def export_arr(self, request, *args, **kwargs):
        sample = self.sample
        debug_print(self.sample.Info.results.isochron['figure_2'])
        export_name = ap.files.arr_file.save(settings.DOWNLOAD_ROOT, sample)
        export_href = '/' + settings.DOWNLOAD_URL + export_name
        messages.info(request, f"Export webarar file (.arr) completed, href: {export_href}")
        return self.JsonResponse({'status': 'success', 'href': export_href})

    def export_xls(self, request, *args, **kwargs):
        template_filepath = os.path.join(settings.SETTINGS_ROOT, 'excel_export_template.xlstemp')
        export_filepath = os.path.join(settings.DOWNLOAD_ROOT, f"{self.sample.Info.sample.name}_export.xlsx")

        try:
            self.sample.to_excel(file_path=export_filepath, template_filepath=template_filepath)
        except (BaseException, Exception) as e:
            debug_print(traceback.format_exc())
            self.error_msg += f'Fail to export excel file (.xls), sample name: {self.sample.Info.sample.name}. Error: {str(e)}'
            messages.error(request, self.error_msg)
            return self.JsonResponse({'msg': self.error_msg}, status=403)
        else:
            export_href = '/' + settings.DOWNLOAD_URL + f"{self.sample.Info.sample.name}_export.xlsx"
            messages.info(request, f'Success to export excel file (.xls), href: {export_href}')
            return self.JsonResponse({'status': 'success', 'href': export_href})

    def export_opju(self, request, *args, **kwargs):
        name = f"{self.sample.Info.sample.name}_export"
        export_filepath = os.path.join(settings.DOWNLOAD_ROOT, f"{name}.opju")
        a = ap.smp.export.CreateOriginGraph(
            name=name, export_filepath=export_filepath, sample=self.sample,
            spectra_data=ap.calc.arr.transpose(self.sample.AgeSpectraPlot.data),
            set1_spectra_data=ap.calc.arr.transpose(self.sample.AgeSpectraPlot.set1.data),
            set2_spectra_data=ap.calc.arr.transpose(self.sample.AgeSpectraPlot.set2.data),
            isochron_data=self.sample.IsochronValues,
            isochron_lines_data=ap.calc.arr.transpose(self.sample.NorIsochronPlot.line1.data) +
                                ap.calc.arr.transpose(self.sample.NorIsochronPlot.line2.data) +
                                ap.calc.arr.transpose(self.sample.InvIsochronPlot.line1.data) +
                                ap.calc.arr.transpose(self.sample.InvIsochronPlot.line2.data) +
                                ap.calc.arr.transpose(self.sample.KClAr1IsochronPlot.line1.data) +
                                ap.calc.arr.transpose(self.sample.KClAr1IsochronPlot.line2.data) +
                                ap.calc.arr.transpose(self.sample.KClAr2IsochronPlot.line1.data) +
                                ap.calc.arr.transpose(self.sample.KClAr2IsochronPlot.line2.data) +
                                ap.calc.arr.transpose(self.sample.KClAr3IsochronPlot.line1.data) +
                                ap.calc.arr.transpose(self.sample.KClAr3IsochronPlot.line2.data),
        )
        try:
            a.get_graphs()
        except (Exception, BaseException) as e:
            self.error_msg += f'Fail to export origin file (.opju), sample name: {self.sample.Info.sample.name}. Error: {str(e)}'
            messages.error(request, self.error_msg)
            return self.JsonResponse({'status': 'fail', 'msg': traceback.format_exc()})
        else:
            export_href = '/' + settings.DOWNLOAD_URL + f"{name}.opju"
            messages.info(request, f'Success to export origin file (.opju), href: {export_href}')
            return self.JsonResponse({'status': 'success', 'href': export_href})

    def export_pdf(self, request, *args, **kwargs):

        figure_id = str(self.body.get('figure_id'))
        merged_pdf = bool(self.body.get('merged_pdf'))
        figure = ap.smp.basic.get_component_byid(self.sample, figure_id)

        name = f"{self.sample.Info.sample.name}_{figure.name}"
        export_filepath = os.path.join(settings.DOWNLOAD_ROOT, f"{name}.pdf")

        if not merged_pdf:
            ap.smp.export.to_pdf(export_filepath, figure_id, self.sample)
        else:
            pass

        export_href = '/' + settings.DOWNLOAD_URL + f"{name}.pdf"

        messages.info(request, f'Success to export pdf, href: {export_href}')
        return self.JsonResponse({'status': 'success', 'href': export_href})

        # Write clipboard
        # import win32clipboard as cp
        # cp.OpenClipboard()
        # # DataObject = 49161
        # # Object Descriptor = 49166
        # # Ole Private Data = 49171
        # # Scalable Vector Graphics = 50148
        # # Portable Document Format = 50199
        # # Scalable Vector Graphics For Adobe Muse = 50215
        # # ADOBE AI3 = 50375
        # # Adobe Illustrator 25.0 = 50376
        # # Encapsulated PostScript = 50379
        # cp.EmptyClipboard()
        # cp.SetClipboardData(cp.RegisterClipboardFormat('Portable Document Format'), pdf_data)
        # cp.CloseClipboard()

    def export_chart(self, request, *args, **kwargs):
        data = self.body['data']
        params = self.body['settings']
        keys = [
            "page_size", "ppi", "width", "height", "pt_width", "pt_height", "pt_left", "pt_bottom",
            "offset_top", "offset_right", "offset_bottom", "offset_left", "plot_together", "show_frame",
        ]
        params = dict(zip(keys, [int(val) if str(val).isnumeric() else val for val in params]))

        file_name = data.get('file_name', 'file_name')
        filepath = f"{settings.DOWNLOAD_URL}{file_name}-{uuid.uuid4().hex[:8]}.pdf"
        filepath = ap.smp.export.export_chart_to_pdf(data, filepath, **params)
        export_href = '/' + filepath

        messages.info(request, f'Success to export_chart, href: {export_href}')
        return self.JsonResponse({'status': 'success', 'href': export_href})

