import copy
import os
import json
import pickle
import traceback
import re

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings

from . import models
from programs import styles, file_funcs, samples, http_funcs, smp_funcs, calc_funcs, basic_funcs, log_funcs
from django.core.cache import cache

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
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open raw file')
        return redirect('open_raw_file_filter')

    def open_arr_file(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open arr file')
        try:
            web_file_path, file_name, extension = \
                file_funcs.get_post_file(request.FILES.get('arr_file'), settings.UPLOAD_ROOT)
            sample = file_funcs.open_arr_file(web_file_path)
        except (Exception, BaseException) as e:
            return render(request, 'calc.html', {
                'title': 'alert', 'type': 'Error', 'message': 'Fail to open the arr file\n' + str(e)
            })
        else:
            return http_funcs.open_object_file(request, sample, web_file_path)

    def open_full_xls_file(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open calc.full file')
        try:
            web_file_path, file_name, extension = \
                file_funcs.get_post_file(request.FILES.get('full_xls_file'), settings.UPLOAD_ROOT)
            file_name = file_name if '.full' not in file_name else file_name.split('.full')[0]
            sample = file_funcs.open_full_xls(web_file_path, samplename=file_name)
        except (Exception, BaseException) as e:
            return render(request, 'calc.html', {
                'title': 'alert', 'type': 'Error', 'message': 'Fail to open the xls file\n' + str(e)
            })
        else:
            return http_funcs.open_object_file(request, sample, web_file_path)

    def open_age_file(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open calc.age file')
        try:
            web_file_path, sample_name, extension = \
                file_funcs.get_post_file(request.FILES.get('age_file'), settings.UPLOAD_ROOT)
            sample = file_funcs.open_age_xls(web_file_path)
        except (Exception, BaseException) as e:
            print(traceback.format_exc())
            return render(request, 'calc.html', {
                'title': 'alert', 'type': 'Error', 'message': 'Fail to open the age file\n' + str(e)
            })
        else:
            return http_funcs.open_object_file(request, sample, web_file_path)

    def open_current_file(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open last file')
        return open_last_object(request)

    def open_new_file(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '001', 'info', 'Open new file')
        sample = samples.Sample()
        # initial settings
        smp_funcs.initial(sample)
        return http_funcs.open_object_file(request, sample, web_file_path='')

    def open_multi_files(self, request, *args, **kwargs):
        msg = ""
        length = int(request.POST.get('length'))
        # print(f"Number of files: {length}")
        files = {}
        for i in range(length):
            file = request.FILES.get(str(i))
            try:
                web_file_path, file_name, suffix = file_funcs.get_post_file(file, settings.UPLOAD_ROOT)
            except (Exception, BaseException) as e:
                msg = msg + f"{file} is not supported. "
                continue
            else:
                files.update({f"multi_files_{i}": {'name': file_name, 'path': web_file_path, 'suffix': suffix}})
        response = HttpResponse(content_type="text/html; charset=utf-8", status=299)
        contents = []
        for key, file in files.items():
            handler = {
                '.arr': file_funcs.open_arr_file, '.xls': file_funcs.open_full_xls,
                '.age': file_funcs.open_age_xls
            }.get(file['suffix'], None)
            try:
                if handler:
                    sample = handler(file['path'], file['name'])
                else:
                    raise TypeError(f"File type {file['suffix']} is not supported: {file['name']}")
            except Exception:
                print(traceback.format_exc())
                continue
            else:
                contents.append(http_funcs.open_object_file(request, sample, file['path']).component)
        response.writelines(contents)
        return response

    @staticmethod
    def get(request, *args, **kwargs):
        # Render calc.html when users are visiting /calc.
        return render(request, 'calc.html')

    def flag_not_matched(self, request, *args, **kwargs):
        # Show calc.html when the received flag doesn't exist.
        log_funcs.set_info_log(self.ip, '001', 'warning', f'Received flag: {self.flag}, it is not matched')
        return render(request, 'calc.html')


class ButtonsResponseObjectView(http_funcs.ArArView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
        ]

    def get(self, request, *args, **kwargs):
        # Visiting /calc/object
        log_funcs.set_info_log(self.ip, '003', 'info', f'GET /calc/object')
        return open_last_object(request)

    def update_sample_photo(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '003', 'info', 'Update sample photo')
        file = request.FILES.get('picture')
        file_funcs.get_post_file(file, os.path.join(settings.STATICFILES_DIRS[0], 'upload'))
        return JsonResponse({'picture': settings.STATIC_URL + 'upload/' + file.name})

    def get_auto_scale(self, request, *args, **kwargs):
        figure_id = self.body['figure_id']
        xscale, yscale = smp_funcs.reset_plot_scale(sample=self.sample, only_figure=figure_id)
        return JsonResponse({
            'status': 'success', 'xMin': xscale[0], 'xMax': xscale[1], 'xInterval': xscale[2],
            'yMin': yscale[0], 'yMax': yscale[1], 'yInterval': yscale[2]
        })

    def update_components_diff(self, request, *args, **kwargs):
        diff = dict(self.body['diff'])
        # print(f"Difference: {diff}")
        for figure_id, attrs in diff.items():
            smp_funcs.update_plot_from_dict(
                smp_funcs.get_component_byid(self.sample, figure_id), attrs)
        # Backup after changes are applied
        components_backup = copy.deepcopy(smp_funcs.get_components(self.sample))
        # Do something for some purpose
        if 'figure_9' in diff.keys() and not all(
                [i not in diff.get('figure_9').keys() for i in ['set1', 'set2', 'set3']]):
            # Histogram plot, replot is required
            smp_funcs.recalc_agedistribution(self.sample)
        res = smp_funcs.get_diff_smp(backup=components_backup, smp=smp_funcs.get_components(self.sample))
        http_funcs.create_cache(self.sample, self.cache_key)  # Update cache
        return JsonResponse(res)

    def click_points_update_figures(self, request, *args, **kwargs):
        series_name = self.body['series_name']
        clicked_data = self.body['clicked_data']
        current_set = self.body['current_set']
        auto_replot = self.body['auto_replot']
        sample = self.sample
        components_backup = copy.deepcopy(smp_funcs.get_components(sample))
        log_funcs.set_info_log(
            self.ip, '003', 'info',
            f'Click a point, series name: {series_name}, clicked data: {clicked_data}, '
            f'set: {current_set}')
        data_index = clicked_data[-1] - 1  # Isochron plot data label starts from 1, not 0
        if series_name == "Unselected Points":
            if current_set == 'set_1':
                sample.SelectedSequence1.append(data_index)
            elif current_set == 'set_2':
                sample.SelectedSequence2.append(data_index)
            sample.UnselectedSequence.remove(data_index)
        elif series_name == "Points Set 1":
            if current_set == 'set_1':
                sample.UnselectedSequence.append(data_index)
                sample.SelectedSequence1.remove(data_index)
            elif current_set == 'set_2':
                sample.SelectedSequence2.append(data_index)
                sample.SelectedSequence1.remove(data_index)
        elif series_name == "Points Set 2":
            if current_set == 'set_2':
                sample.UnselectedSequence.append(data_index)
                sample.SelectedSequence2.remove(data_index)
            elif current_set == 'set_1':
                sample.SelectedSequence1.append(data_index)
                sample.SelectedSequence2.remove(data_index)
        sample.IsochronMark = [
            1 if i in sample.SelectedSequence1 else 2 if i in sample.SelectedSequence2 else '' for i in
            range(len(sample.IsochronValues[2]))]
        # Update isochron table data
        smp_funcs.get_component_byid(sample, '7').data = basic_funcs.setTableData(
            sample.SequenceName, sample.SequenceValue, sample.IsochronMark, *sample.IsochronValues)
        if auto_replot:
            smp_funcs.recalculate(sample, re_plot=True, isInit=False, isIsochron=True, isPlateau=True)  # Replot after clicking points
        http_funcs.create_cache(sample, self.cache_key)  # 更新缓存
        # Response are changes in sample.Components, in this way we can decrease the size of response.
        res = smp_funcs.get_diff_smp(backup=components_backup, smp=smp_funcs.get_components(sample))
        if '7' in res.keys():
            res.pop('7')
        res.update({'marks': sample.IsochronMark})
        return JsonResponse({'res': basic_funcs.getJsonDumps(res)})

    def update_handsontable(self, request, *args, **kwargs):
        btn_id = str(self.body['btn_id'])
        recalculate = self.body['recalculate']  # This is always False
        data = self.body['data']
        sample = self.sample
        log_funcs.set_info_log(
            self.ip, '003', 'info', f'Update handsontable, sample name: {sample.Info.sample.name}, '
            f'btn id: {btn_id}'
        )
        # backup for later comparision
        components_backup = copy.deepcopy(smp_funcs.get_components(sample))
        if btn_id == '0':  # 实验信息
            # sample.Info.__dict__.update(data)
            smp_funcs.update_plot_from_dict(sample.Info, data)
        else:

            def _get_max_row(a: list):
                res = 0
                for i in range(len(a)):
                    if not basic_funcs.thisListIsEmpty(a[i]):
                        res = i
                return res

            def _normalize_data(a, cols, start_col=0):
                if len(a) >= cols:
                    return a[start_col:cols]
                else:
                    return a[start_col:]+ [[''] * len(a[0])] * (cols - len(a))

            def _strToBool(a, cols):
                bools = [True, False, '']
                strs = ['True', 'False', '']
                for col in cols:
                    a[col] = [bools[strs.index(item.capitalize())] if isinstance(item, str) else item for item in
                              a[col]]
                return a

            max_col = max([len(i) for i in data])
            max_row = _get_max_row(data)
            data = basic_funcs.getPartialArry(
                basic_funcs.getTransposed(data), 0, max_row + 1, *[i for i in range(max_col)])
            if len(data) == 0:
                return JsonResponse({})
            sample.SequenceName = data[0]
            sample.SequenceValue = data[1]
            if btn_id == '1':  # 样品值
                data = _normalize_data(data, 12, 2)
                sample.SampleIntercept = data
            elif btn_id == '2':  # 本底值
                data = _normalize_data(data, 12, 2)
                sample.BlankIntercept = data
            elif btn_id == '3':  # 校正值
                data = _normalize_data(data, 12, 2)
                sample.CorrectedValues = data
            elif btn_id == '4':  #
                data = _normalize_data(data, 34, 2)
                sample.DegasValues = data
            elif btn_id == '5':  # 发行表
                data = _normalize_data(data, 13, 2)
                sample.PublishValues = data
            elif btn_id == '6':  # 年龄谱
                data = _normalize_data(data, 10, 2)
                sample.ApparentAgeValues = data
            elif btn_id == '7':  # 等时线
                sample.IsochronMark = data[2]
                data = _normalize_data(data, 42, 3)
                sample.IsochronValues = data
                sample.SelectedSequence1 = [
                    i for i in range(len(sample.IsochronMark)) if sample.IsochronMark[i] == 1]
                sample.SelectedSequence2 = [
                    i for i in range(len(sample.IsochronMark)) if sample.IsochronMark[i] == 2]
                sample.UnselectedSequence = [
                    i for i in range(len(sample.IsochronMark)) if i not in sample.SelectedSequence1 + sample.SelectedSequence2]
            elif btn_id == '8':  # 总参数
                data = _strToBool(_normalize_data(data, 120, 2), list(range(101, 114)))
                sample.TotalParam = data
                sample.AgeSpectraPlot.initial_params.update({
                    'useInputInitial': [
                        sample.TotalParam[0][0], sample.TotalParam[1][0] * sample.TotalParam[0][0] / 100,
                        sample.TotalParam[0][0], sample.TotalParam[1][0] * sample.TotalParam[0][0] / 100
                    ]
                })
            smp_funcs.update_table_data(sample)  # Update data of tables after changes of a table
            if btn_id == '7':
                # Re-calculate isochron and plateau data, and replot.
                # Re-calculation will not be applied automatically when other tables were changed
                smp_funcs.recalculate(sample, re_plot=True, isInit=False, isIsochron=True, isPlateau=True)  # Change isochron mark

        http_funcs.create_cache(sample, self.cache_key)  # Update cache
        res = smp_funcs.get_diff_smp(components_backup, smp_funcs.get_components(sample))
        return JsonResponse({'changed_components': basic_funcs.getJsonDumps(res)})

    def export_arr(self, request, *args, **kwargs):
        sample = self.sample
        export_name = file_funcs.save_webarar_file(settings.DOWNLOAD_ROOT, sample)
        export_href = '/' + settings.DOWNLOAD_URL + export_name
        log_funcs.set_info_log(self.ip, '003', 'info',
                          f'Success to export webarar file (.arr), sample name: {sample.Info.sample.name}, '
                          f'export href: {export_href}')
        return JsonResponse({'status': 'success', 'href': export_href})

    def export_xls(self, request, *args, **kwargs):
        template_filepath = os.path.join(settings.SETTINGS_ROOT, 'excel_export_template.xlstemp')
        export_filepath = os.path.join(settings.DOWNLOAD_ROOT, f"{self.sample.Info.sample.name}_export.xlsx")
        default_style = {
            'font_size': 10, 'font_name': 'Microsoft Sans Serif', 'bold': False,
            'bg_color': '#FFFFFF',  # back ground
            'font_color': '#000000', 'align': 'left',
            'top': 1, 'left': 1, 'right': 1, 'bottom': 1  # border width
        }
        a = file_funcs.WritingWorkbook(
            filepath=export_filepath, style=default_style, template_filepath=template_filepath, sample=self.sample)
        res = a.get_xls()
        export_href = '/' + settings.DOWNLOAD_URL + f"{self.sample.Info.sample.name}_export.xlsx"
        if res:
            log_funcs.set_info_log(
                self.ip, '003', 'info', f'Success to export excel file (.xls), '
                                        f'sample name: {self.sample.Info.sample.name}, export href: {export_href}')
            return JsonResponse({'status': 'success', 'href': export_href})
        else:
            log_funcs.set_info_log(self.ip, '003', 'info',
                 f'Fail to export excel file (.xls), sample name: {self.sample.Info.sample.name}')
            return JsonResponse({'status': 'fail', 'msg': res})

    def export_opju(self, request, *args, **kwargs):
        name = f"{self.sample.Info.sample.name}_export"
        export_filepath = os.path.join(settings.DOWNLOAD_ROOT, f"{name}.opju")
        a = file_funcs.CreateOriginGraph(
            name=name, export_filepath=export_filepath, sample=self.sample,
            spectra_data=basic_funcs.getTransposed(self.sample.AgeSpectraPlot.data),
            set1_spectra_data=basic_funcs.getTransposed(self.sample.AgeSpectraPlot.set1.data),
            set2_spectra_data=basic_funcs.getTransposed(self.sample.AgeSpectraPlot.set2.data),
            isochron_data=self.sample.IsochronValues,
            isochron_lines_data=basic_funcs.getTransposed(self.sample.NorIsochronPlot.line1.data) +
            basic_funcs.getTransposed(self.sample.NorIsochronPlot.line2.data) +
            basic_funcs.getTransposed(self.sample.InvIsochronPlot.line1.data) +
            basic_funcs.getTransposed(self.sample.InvIsochronPlot.line2.data) +
            basic_funcs.getTransposed(self.sample.KClAr1IsochronPlot.line1.data) +
            basic_funcs.getTransposed(self.sample.KClAr1IsochronPlot.line2.data) +
            basic_funcs.getTransposed(self.sample.KClAr2IsochronPlot.line1.data) +
            basic_funcs.getTransposed(self.sample.KClAr2IsochronPlot.line2.data) +
            basic_funcs.getTransposed(self.sample.KClAr3IsochronPlot.line1.data) +
            basic_funcs.getTransposed(self.sample.KClAr3IsochronPlot.line2.data),
        )
        try:
            res = a.get_graphs()
        except Exception:
            res = traceback.format_exc()
            log_funcs.set_info_log(
                self.ip, '003', 'info',
                f'Fail to export origin file (.opju), sample name: {self.sample.Info.sample.name}')
            return JsonResponse({'status': 'fail', 'msg': res})
        else:
            export_href = '/' + settings.DOWNLOAD_URL + f"{name}.opju"
            log_funcs.set_info_log(self.ip, '003', 'info', f'Success to export origin file (.opju), '
                                                      f'sample name: {self.sample.Info.sample.name}, '
                                                      f'export href: {export_href}')
            return JsonResponse({'status': 'success', 'href': export_href})

    def export_pdf(self, request, *args, **kwargs):

        figure_id = str(self.body.get('figure_id'))
        merged_pdf = bool(self.body.get('merged_pdf'))
        figure = smp_funcs.get_component_byid(self.sample, figure_id)

        name = f"{self.sample.Info.sample.name}_{figure.name}"
        export_filepath = os.path.join(settings.DOWNLOAD_ROOT, f"{name}.pdf")

        # filepath = 'D:\\Downloads\\2.pdf'
        # with open(filepath, 'rb') as f:
        #     pdf_data: bytes = f.read()

        # Do something for PDF BODY
        if not merged_pdf:
            file_funcs.CreatePDF(
                name=f"{self.sample.Info.sample.name}_export",
                export_filepath=export_filepath,
                sample=self.sample,
                figure=figure,
            ).get_pdf()
        else:
            pdf1 = file_funcs.CreatePDF(
                name=f"{self.sample.Info.sample.name}_export",
                export_filepath=export_filepath,
                sample=self.sample,
                figure=smp_funcs.get_component_byid(self.sample, 'figure_1'),
                axis_area=[60, 400, 200, 160]
            ).get_contents()

            pdf2 = file_funcs.CreatePDF(
                name=f"{self.sample.Info.sample.name}_export",
                export_filepath=export_filepath,
                sample=self.sample,
                figure=smp_funcs.get_component_byid(self.sample, 'figure_2'),
                axis_area=[320, 400, 200, 160]
            ).get_contents()

            pdf3 = file_funcs.CreatePDF(
                name=f"{self.sample.Info.sample.name}_export",
                export_filepath=export_filepath,
                sample=self.sample,
                figure=samples.Plot(name='Merged'),
                component=pdf1['component']+pdf2['component'],
                text=pdf1['text']+pdf2['text'],
                frame=pdf1['frame']+pdf2['frame']
            )
            pdf3.set_info()
            pdf3.set_replace()
            pdf3.toBetys()
            pdf3.save()
            
        export_href = '/' + settings.DOWNLOAD_URL + f"{name}.pdf"

        return JsonResponse({'status': 'success', 'href': export_href})

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

    def get_regression_result(self, request, *args, **kwargs):
        data = list(self.body.get('data'))
        method = str(self.body.get('method'))
        adjusted_x = list(self.body.get('x'))
        x, adjusted_time = [], []
        year, month, day, hour, min, second = re.findall("(.*)-(.*)-(.*)T(.*):(.*):(.*)", data[0][0])[0]
        for each in data[0]:
            x.append(calc_funcs.get_datetime(
                *re.findall("(.*)-(.*)-(.*)T(.*):(.*):(.*)", each)[0],
                base=[int(year), int(month), int(day), int(hour), int(min)]
            ))
        for each in adjusted_x:
            adjusted_time.append(calc_funcs.get_datetime(
                *re.findall("(.*)-(.*)-(.*)T(.*):(.*):(.*)", each)[0],
                base=[int(year), int(month), int(day), int(hour), int(min)]
            ))
        y = data[1]
        handler = {
            'linear': calc_funcs.intercept_linest,
            'average': calc_funcs.intercept_average,
            'quadratic': calc_funcs.intercept_quadratic,
            'polynomial': calc_funcs.intercept_polynomial,
            'power': calc_funcs.intercept_power,
            'exponential': calc_funcs.intercept_exponential,
        }
        if method in handler.keys():
            try:
                handler = handler[method]
                res = handler(y, x)
            except:
                print(traceback.format_exc())
                res = False
            if res:
                line_data = [adjusted_x, res[7](adjusted_time)]
                return JsonResponse({'r2': res[3], 'line_data': line_data, 'sey': res[8]})
        return JsonResponse({'r2': 'None', 'line_data': [], 'sey': 'None'})

    def change_initial_ratio_for_plateaus(self, request, *args, **kwargs):
        initial_params = self.body['initial_params']
        sample = self.sample
        # backup for later comparision
        components_backup = copy.deepcopy(smp_funcs.get_components(sample))
        log_funcs.set_info_log(
            self.ip, '003', 'info', f'Update calc params, sample name: {self.sample.Info.sample.name}')
        if sample.AgeSpectraPlot.initial_params == initial_params:
            return JsonResponse({'status': False})
        else:
            sample.AgeSpectraPlot.initial_params.update(initial_params)
            smp_funcs.recalculate(sample, re_plot=True, isIsochron=False, isInit=False, isPlateau=True)  # Replot plateau after changes of initial ratio
            http_funcs.create_cache(sample, self.cache_key)  # 更新缓存
            res = smp_funcs.get_diff_smp(backup=components_backup, smp=smp_funcs.get_components(sample))
            # print(f"Diff after change initial ratio: {res}")
            return JsonResponse({'status': True, 'changed_components': basic_funcs.getJsonDumps(res)})

    def set_params(self, request, *args, **kwargs):
        def remove_none(old_params, new_params, rows, length):
            res = [[]] * length
            for index, item in enumerate(new_params):
                if item is None:
                    res[index] = old_params[index]
                else:
                    res[index] = [item] * rows
            return res
        params = list(self.body['params'])
        type = str(self.body['type'])  # type = 'irra', or 'calc', or 'smp'
        sample = self.sample
        log_funcs.set_info_log(
            self.ip, '003', 'info', f'Set params, sample name: {self.sample.Info.sample.name}')
        # backup for later comparision
        components_backup = copy.deepcopy(smp_funcs.get_components(sample))
        # 检查arr版本
        # sample = file_funcs.check_arr_version(sample)
        n = len(sample.SequenceName)
        # Do something to set params
        if type == 'calc':
            sample.TotalParam[34:56] = remove_none(sample.TotalParam[34:56], params[0:22], n, 56-34)
            sample.TotalParam[71:97] = remove_none(sample.TotalParam[71:97], params[22:48], n, 97-71)
        elif type == 'irra':

            sample.TotalParam[0:20] = remove_none(sample.TotalParam[0:20], params[0:20], n, 20-0)
            sample.TotalParam[56:58] = remove_none(sample.TotalParam[56:58], params[20:22], n, 57-55)  # Cl36/38 productivity
            sample.TotalParam[20:27] = remove_none(sample.TotalParam[20:27], params[22:29], n, 27-20)
            # sample.TotalParam[26] = [params[26]] * n
            irradiation_time = []
            duration = []
            if None not in params[29:-3] and '' not in params[29:-3]:
                for i in range(len(params[29:-3])):
                    if i % 2 == 0:
                        [d, t] = params[29:-3][i].split('T')
                        [t1, t2] = t.split(':')
                        irradiation_time.append(d + '-' + t1 + '-' + t2 + 'D' + str(params[29:-3][i + 1]))
                        duration.append(params[29:-3][i + 1])
                sample.TotalParam[27] = ['S'.join(irradiation_time)] * n
                sample.TotalParam[28] = [params[-3]] * n
                sample.TotalParam[29] = [sum(duration)] * n
            if params[-5] != '':
                [a, b] = params[-5].split('T')
                [b, c] = b.split(':')
                sample.TotalParam[30] = [a + '-' + b + '-' + c] * n
            try:
                stand_time_second = [
                    calc_funcs.get_datetime(*sample.TotalParam[31][i].split('-')) - calc_funcs.get_datetime(
                        *sample.TotalParam[30][i].split('-')) for i in range(n)]
            except Exception as e:
                print(f'Error in calculate standing duration: {traceback.format_exc()}')
            else:
                sample.TotalParam[32] = [i / (3600 * 24 * 365.242) for i in stand_time_second]  # stand year

        elif type == 'smp':
            sample.TotalParam[67:71] = remove_none(sample.TotalParam[67:71], params[0:4], n, 71-67)
            sample.TotalParam[58:67] = remove_none(sample.TotalParam[58:67], params[4:13], n, 67-58)
            sample.TotalParam[97:100] = remove_none(sample.TotalParam[97:100], params[13:16], n, 100-97)
            sample.TotalParam[100:114] = remove_none(
                sample.TotalParam[100:114],
                [['Linear', 'Exponential', 'Power'][params[16:19].index(True)], *params[19:32]], n, 114-100)
        else:
            return JsonResponse({'status': 'fail', 'msg': f'Unknown type of params : {type}'})
        smp_funcs.update_table_data(sample)  # Update data of tables after changes of calculation parameters
        # update cache
        http_funcs.create_cache(sample, self.cache_key)
        res = smp_funcs.get_diff_smp(backup=components_backup, smp=smp_funcs.get_components(sample))
        # print(f"Diff after reset_calc_params: {res}")
        return JsonResponse({'status': 'success', 'msg': 'Successfully!', 'changed_components': basic_funcs.getJsonDumps(res)})

    def recalculation(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '003', 'info', f'Recalculation, sample name: {self.sample.Info.sample.name}')
        sample = self.sample
        checked_options = self.body['checked_options']
        # backup for later comparision
        components_backup = copy.deepcopy(smp_funcs.get_components(sample))
        try:
            sample = smp_funcs.recalculate(sample, *checked_options)  # Re-calculating based on selected options
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'status': 'fail', 'msg': f'Error in recalculating: {e}'})
        smp_funcs.update_table_data(sample)  # Update data of tables after re-calculation
        # Update cache
        http_funcs.create_cache(sample, self.cache_key)
        res = smp_funcs.get_diff_smp(backup=components_backup, smp=smp_funcs.get_components(sample))
        # print(f"Diff after recalculation: {res}")
        return JsonResponse({
            'status': 'success', 'msg': "Success to recalculate",
            'changed_components': basic_funcs.getJsonDumps(res)
        })

    def calc_change_irra_projects(self, request, *args, **kwargs):
        try:
            name = self.body['name']
            param_file = models.IrraParams.objects.get(name=name).file_path
            param = file_funcs.read_setting_file(param_file)
            log_funcs.set_info_log(self.ip, '003', 'info',
                              f'Change irra params projects, sample name: {self.sample.Info.sample.name}, '
                              f'param name: {name}, param server path: {param_file}')
            return JsonResponse({'status': 'success', 'param': param})
        except KeyError:
            sample = self.sample
            data = basic_funcs.getTransposed(sample.TotalParam)[0]
            param = [*data[0:27], *basic_funcs.getIrradiationDatetimeByStr(data[27]), data[28], '', '']
            log_funcs.set_info_log(self.ip, '003', 'info',
                              f'Irra param project is not found in database, using params in total param values, '
                              f'sample name: {self.sample.Info.sample.name}')
            return JsonResponse({'status': 'success', 'param': param})
        except Exception as e:
            log_funcs.set_info_log(self.ip, '003', 'info', f'Fail to change irra params projects')
            return JsonResponse({'status': 'fail', 'msg': 'no param project exists in database' + str(e)})

    def calc_change_calc_projects(self, request, *args, **kwargs):
        try:
            name = self.body['name']
            param_file = models.CalcParams.objects.get(name=name).file_path
            param = file_funcs.read_setting_file(param_file)
            log_funcs.set_info_log(self.ip, '003', 'info',
                              f'Change calc params projects, sample name: {self.sample.Info.sample.name}, '
                              f'param name: {name}, param server path: {param_file}')
            return JsonResponse({'status': 'success', 'param': param})
        except KeyError:
            sample = self.sample
            data = basic_funcs.getTransposed(sample.TotalParam)[0]
            param = [*data[34:100], *basic_funcs.getMethodFittingLawByStr(data[100]), *data[101:114]]
            log_funcs.set_info_log(self.ip, '003', 'info',
                              f'Calc param project is not found in database, using params in total param values, '
                              f'sample name: {self.sample.Info.sample.name}')
            return JsonResponse({'status': 'success', 'param': param})
        except Exception as e:
            log_funcs.set_info_log(self.ip, '003', 'info', f'Fail to change calc params projects')
            return JsonResponse({'status': 'fail', 'msg': 'no param project exists in database. ' + str(e)})

    def flag_not_matched(self, request, *args, **kwargs):
        # Show calc.html when the received flag doesn't exist.
        return open_last_object(request)


class RawFileView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
            "submit",
            "close",
            "upload_raw_project",
            'raw_files_submit',
        ]

    def get(self, request, *args, **kwargs):
        # Visiting /calc/raw
        log_funcs.set_info_log(self.ip, '004', 'info', f'Open raw file filter')
        return render(request, 'raw_filter.html')

    def flag_not_matched(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '004', 'info', f'Flag is not matched')
        return redirect('calc_view')

    def raw_files_changed(self, request, *args, **kwargs):
        files = []
        filter = request.POST.get('fileOptionsRadios')
        for file in request.FILES.getlist('raw_file'):
            try:
                web_file_path, file_name, suffix = file_funcs.get_post_file(file, settings.UPLOAD_ROOT)
            except Exception:
                continue
            else:
                files.append({
                    'name': file_name, 'extension': suffix, 'path': web_file_path,
                    'filter': suffix[1:] if filter == 'auto' else filter
                })
        return JsonResponse({'files': files})

    def submit(self, request, *args, **kwargs):
        files = json.loads(request.POST.get('raw-file-table'))['files']
        step_list = []
        sequenceName = []
        for file in files:
            each_list = file_funcs.open_raw_file(file['file_path'], file['filter'])
            if not each_list:  # Wrong files
                return redirect('calc_view')
            step_list = step_list + each_list
            sequenceName = sequenceName + [file['file_name'] + "-" + str(i+1) for i in range(len(each_list))]

        def _get_experiment_time(time_str):
            k1 = time_str.split(' ')
            [month, day, year] = k1[0].split('/')
            [hour, min, second] = k1[2].split(':')
            if 'pm' in time_str.lower() and int(hour) < 12:
                hour = int(hour) + 12
            if 'am' in time_str.lower() and int(hour) >= 12:
                hour = int(hour) - 12
            return f'{year}-{month}-{day}T{hour}:{min}:{second}'

        def _is_blank(label: str):
            return True if label.capitalize() in ['Blk', 'B', 'Blank'] else False

        selectedData = [[[]]]
        unselectedData = [[[]]]
        experimentTime = []
        sequenceLabel = []
        isBlank = []
        if step_list:
            selectedData = [[
                [[j[9], j[10]] for j in i[1:]],  # Ar36
                [[j[7], j[8]] for j in i[1:]],  # Ar37
                [[j[5], j[6]] for j in i[1:]],  # Ar38
                [[j[3], j[4]] for j in i[1:]],  # Ar39
                [[j[1], j[2]] for j in i[1:]],  # Ar40
            ] for i in step_list]
            unselectedData = [[[], [], [], [], []] for i in step_list]
            experimentTime = [_get_experiment_time(i[0][1]) for i in step_list]
            sequenceLabel = [i[0][3] for i in step_list]
            isBlank = [_is_blank(i[0][2]) for i in step_list]

        res = [file_funcs.get_lines_data(i) for i in selectedData]
        linesData = [i[0] for i in res]
        linesResults = [i[1] for i in res]
        fitMethod = [[0 for j in range(5)] for i in range(len(linesResults))]

        raw_data = {
            'selectedData': selectedData, 'unselectedData': unselectedData, 'linesData': linesData,
            'linesResults': linesResults, 'fitMethod': fitMethod, 'sequenceLabel': sequenceLabel,
            'experimentTime': experimentTime, 'sequenceName': sequenceName, 'isBlank': isBlank
        }
        allIrraNames = list(models.IrraParams.objects.values_list('name', flat=True))
        allCalcNames = list(models.CalcParams.objects.values_list('name', flat=True))
        allSmpNames = list(models.SmpParams.objects.values_list('name', flat=True))

        return render(request, 'extrapolate.html', {
            'data': json.dumps(raw_data, cls=basic_funcs.MyEncoder, indent=4),
            'allIrraNames': allIrraNames, 'allCalcNames': allCalcNames, 'allSmpNames': allSmpNames
        })

    def import_blank_file(self, request, *args, **kwargs):
        file = request.FILES.get('blank_file')
        web_file_path, file_name, suffix = file_funcs.get_post_file(file, settings.UPLOAD_ROOT)
        new_blank_sequence = {
            'name': ['Test'],
            'experimentTime': ["2024-6-9-18-40-22"],
            'Ar36': [[0.4790974808856151, 0.011707830326843962, 2.443726129638994, 0.5894056663608368]],
            'Ar37': [[0.5106817066057479, 0.015751668730122223, 3.0844395885679714, 0.7801597508113187]],
            'Ar38': [[0.5106817066057479, 0.015751668730122223, 3.0844395885679714, 0.7801597508113187]],
            'Ar39': [[0.5106817066057479, 0.015751668730122223, 3.0844395885679714, 0.7801597508113187]],
            'Ar40': [[0.5106817066057479, 0.015751668730122223, 3.0844395885679714, 0.7801597508113187]],
        }
        return JsonResponse({"new_blank": new_blank_sequence})

    def raw_files_submit(self, request, *args, **kwargs): # 之前的打开单个文件的submit
        web_file_path, file_name, _ = file_funcs.get_post_file(request.FILES.get('raw_file'), settings.UPLOAD_ROOT)
        log_funcs.set_info_log(self.ip, '004', 'info', f'Start to submit raw file, file name: {file_name}, '
                                                  f'server file path: {web_file_path}')

        step_list = file_funcs.open_raw_file(web_file_path)

        def _get_experiment_time(time_str):
            k1 = time_str.split(' ')
            [month, day, year] = k1[0].split('/')
            [hour, min, second] = k1[2].split(':')
            if 'pm' in time_str.capitalize():
                hour = int(hour) + 12
            return "-".join([year, month, day, str(hour), min, second])

        def _is_blank(label: str):
            return True if label.capitalize() in ['Blk', 'B', 'Blank'] else False

        selectedData = [[[]]]
        unselectedData = [[[]]]
        experimentTime = []
        sequenceLabel = []
        isBlank = []
        sequenceName = []
        if step_list:
            selectedData = [[
                [[j[1], j[6]] for j in i[1:]],  # Ar36
                [[j[1], j[5]] for j in i[1:]],  # Ar37
                [[j[1], j[4]] for j in i[1:]],  # Ar38
                [[j[1], j[3]] for j in i[1:]],  # Ar39
                [[j[1], j[2]] for j in i[1:]]] for i in step_list]  # Ar40
            unselectedData = [[[], [], [], [], []] for i in step_list]
            experimentTime = [_get_experiment_time(i[0][1]) for i in step_list]
            sequenceLabel = [i[0][3] for i in step_list]
            isBlank = [_is_blank(i[0][2]) for i in step_list]
            sequenceName = [file_name + "-" + str(i+1) for i in range(len(step_list))]

        res = [file_funcs.get_lines_data(i) for i in selectedData]
        linesData = [i[0] for i in res]
        linesResults = [i[1] for i in res]
        fitMethod = [[0 for j in range(5)] for i in range(len(linesResults))]
        # 写入缓存
        raw_data = {
            'selectedData': selectedData, 'unselectedData': unselectedData, 'linesData': linesData,
            'linesResults': linesResults, 'fitMethod': fitMethod, 'sequenceLabel': sequenceLabel,
            'experimentTime': experimentTime, 'sequenceName': sequenceName, 'isBlank': isBlank
        }
        allIrraNames = list(models.IrraParams.objects.values_list('name', flat=True))
        allCalcNames = list(models.CalcParams.objects.values_list('name', flat=True))
        allSmpNames = list(models.SmpParams.objects.values_list('name', flat=True))

        log_funcs.set_info_log(self.ip, '004', 'info', f'Success to submit raw file')
        return render(request, 'extrapolate.html', {
            'data': json.dumps(raw_data),
            'allIrraNames': allIrraNames, 'allCalcNames': allCalcNames, 'allSmpNames': allSmpNames
        })

    def close(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '004', 'info', f'Close')
        return redirect('calc_view')

    def upload_raw_project(self, request, *args, **kwargs):
        log_funcs.set_info_log(self.ip, '004', 'info', f'Upload raw project')
        return open_last_object(request)
        # return redirect('object_views_2')

    def raw_fit_method_changed(self, request, *args, **kwargs):
        fitMethod = self.body['fitMethod']
        fitMethodValue = self.body['fitMethodValue']
        fitMethodForAll = self.body['fitMethodForAll']
        sequence = self.body['sequence']
        isotope = self.body['isotope']
        log_funcs.set_info_log(self.ip, '004', 'info', f'Change raw fit method')
        if fitMethodForAll:
            for i in range(len(fitMethod)):
                for j in range(5):
                    fitMethod[i][j] = fitMethodValue
        else:
            fitMethod[sequence][isotope] = fitMethodValue
        return JsonResponse({'fitMethod': fitMethod})

    def raw_corr_blank_method_changed(self, request, *args, **kwargs):
        receive = json.loads(request.body.decode('utf-8'))
        method = receive['corrBlankMethod']
        isBlank = receive['isBlank']

        log_funcs.set_info_log(self.ip, '004', 'info', f'Change correct blank method')

        def _get_corr_relation(a: list, m: int or str):
            _blank, _unknown = [], []
            for index, val in enumerate(a):
                if val:
                    _blank.append(index)
                else:
                    _unknown.append(index)
            if str(m) == '0':  # 向下校正
                for j in _blank:
                    if _blank.index(j) == len(_blank) - 1:
                        continue
                    if j == _blank[_blank.index(j) + 1]:
                        _blank.remove(j)
                for i, v in enumerate(_unknown):
                    try:
                        if v < _blank[i]:
                            _blank.insert(i, _blank[i - 1])
                    except IndexError:
                        _blank.insert(i, _blank[i - 1])
                _blank = _blank[0:len(_unknown)]
            elif str(m) == '1':  # 向上校正
                res = []
                for i, v in enumerate(_unknown):
                    for j in _blank:
                        if v < j:
                            res.append(j)
                            break
                for i in range(len(_unknown) - len(res)):
                    res.append(_blank[-1])
                _blank = res
            elif str(m) == '2':  # 临近扣除
                res = []
                for i, v in enumerate(_unknown):
                    if v < _blank[0]:
                        res.append(_blank[0])
                        continue
                    elif v > _blank[-1]:
                        res.append((_blank[-1]))
                        continue
                    for j in range(len(_blank) - 1):
                        if _blank[j + 1] - v >= v - _blank[j] > 0:
                            res.append(_blank[j])
                            break
                        elif v - _blank[j] > _blank[j + 1] - v > 0:
                            res.append(_blank[j + 1])
                            break
                _blank = res
            else:  # interpolation
                _blank = [-1] * len(_unknown)
            return _unknown, _blank

        unknown, blank = _get_corr_relation(isBlank, method)
        return JsonResponse({'blankIndex': blank})

    def calc_raw_chart_clicked(self, request, *args, **kwargs):
        selectedData = self.body['selectedData']
        unselectedData = self.body['unselectedData']
        clickedData = self.body['clickedData']
        seriesName = self.body['series']
        isotope = self.body['isotope']
        selectionForAll = self.body['selectionForAll']

        log_funcs.set_info_log(self.ip, '004', 'info', f'Click a point in the raw chart')
        # 备份数据
        selectedData_backup = copy.deepcopy(selectedData)
        unselectedData_backup = copy.deepcopy(unselectedData)
        error = ''

        def _change_list(_isotope):
            _a = selectedData[isotope] + unselectedData[isotope]
            _a.sort(key=lambda a0: a0[0])
            _index = _a.index(clickedData)
            _totalData = selectedData[_isotope] + unselectedData[_isotope]
            _totalData.sort(key=lambda a0: a0[0])
            _indexFilledPoints = _totalData[_index] in selectedData[_isotope]
            if seriesName == 'Filled Points':
                if _indexFilledPoints:
                    selectedData[_isotope].remove(_totalData[_index])
                    unselectedData[_isotope].append(_totalData[_index])
                    selectedData[_isotope].sort(key=lambda a0: a0[0])
                    unselectedData[_isotope].sort(key=lambda a0: a0[0])
                else:
                    pass
            if seriesName == 'Unfilled Points':
                if _indexFilledPoints:
                    pass
                else:
                    unselectedData[_isotope].remove(_totalData[_index])
                    selectedData[_isotope].append(_totalData[_index])
                    unselectedData[_isotope].sort(key=lambda a0: a0[0])
                    selectedData[_isotope].sort(key=lambda a0: a0[0])
            if len(selectedData[_isotope]) < 4:
                return False
            return True

        if selectionForAll:
            for i in range(5):
                if not _change_list(_isotope=i):
                    selectedData = copy.deepcopy(selectedData_backup)
                    unselectedData = copy.deepcopy(unselectedData_backup)
                    error = '选择点不能少于4个'
                    log_funcs.set_info_log(self.ip, '004', 'info', f'Operation is prohibited, the number of selected points will be lesser than 4')
                    break
        else:
            if not _change_list(_isotope=isotope):
                selectedData = copy.deepcopy(selectedData_backup)
                unselectedData = copy.deepcopy(unselectedData_backup)
                error = '选择点不能少于4个'
                log_funcs.set_info_log(self.ip, '004', 'info',
                                  f'Operation is prohibited, the number of selected points will be lesser than 4')
        linesData, linesResults = file_funcs.get_lines_data(selectedData)
        return JsonResponse({
            'selectedData': selectedData,
            'unselectedData': unselectedData,
            'linesData': linesData,
            'linesResults': linesResults,
            'error': error})

    def calc_raw_average_blanks(self, request, *args, **kwargs):
        blanks = self.body['blanks']
        log_funcs.set_info_log(
            self.ip, '004', 'info',
            f'Calculate average value of selected blanks, '
            f'the number of selected points will be lesser than 4')
        newBlank = []
        for i in range(5):
            _intercept = sum([j[i]['intercept'] for j in blanks]) / len(blanks)
            _err = calc_funcs.error_div((_intercept, calc_funcs.error_add(*[j[i]['absolute err'] for j in blanks])), (len(blanks), 0))
            _relative_err = _err / _intercept * 100
            isotope = {
                'isotope': ["Ar36", "Ar37", "Ar38", "Ar39", "Ar40"][i],
                'intercept': _intercept, 'absolute err': _err, 'relative err': _relative_err, 'r2': None, 'mswd': None
            }
            newBlank.append(isotope)
        return JsonResponse({'newBlank': newBlank})


    def calc_raw_submit(self, request, *args, **kwargs):
        """
        Raw data submit, return a sample instance and render a object html.
        """
        irradiationParams = self.body['irradiationParams']
        calculationParams = self.body['calculationParams']
        sampleParams = self.body['sampleParams']
        sampleInfo = self.body['sampleInfo']
        interceptData = self.body['interceptData']
        fingerprint = self.body['fingerprint']
        log_funcs.set_info_log(self.ip, '004', 'info', f'Start to submit raw file')

        # 创建sample
        sample = samples.Sample()
        # Initial values
        smp_funcs.initial(sample)
        # experimental time, unknown and blank intercepts
        unknown_intercept, blank_intercept = [], []
        experimentTime = []
        for row in interceptData:
            experimentTime.append(row['experimentTime'])
            unknown_intercept.append(row['unknownData'])
            blank_intercept.append(row['blankData'])
            sample.SequenceName.append(row['unknown'])
            sample.SequenceValue.append(row['label'])
        sample.SampleIntercept = basic_funcs.getTransposed(unknown_intercept)
        sample.BlankIntercept = basic_funcs.getTransposed(blank_intercept)
        # sample info
        info = {
            'sample': {'name': sampleInfo[0], 'material': sampleInfo[1], 'location': sampleInfo[2]},
            'researcher': {'name': sampleInfo[3]},
            'laboratory': {'name': sampleInfo[4], 'info': sampleInfo[5], 'analyst': sampleInfo[6]}
        }
        smp_funcs.update_plot_from_dict(sample.Info, info)
        # Params
        calc_params = calculationParams['param']
        irra_params = irradiationParams['param']
        smp_params = sampleParams['param']
        irradiation = [item for index, item in enumerate(irra_params[29:-3]) if index % 2 == 0]
        def repleceString(text):
            for char in ['T', ':']:
                text = text.replace(char, '-')
            return text
        irradiation = [repleceString(each) for each in irradiation]
        duration = [item for index, item in enumerate(irra_params[29:-3]) if index % 2 == 1]
        cycle = [irradiation[i] + 'D' + str(duration[i]) for i in range(len(irradiation))]
        sample.TotalParam = basic_funcs.getTransposed(
            [[
                *irra_params[0:26],
                int(irra_params[28]),  # cycle count
                'S'.join(cycle),
                irra_params[-3], sum(duration), irradiation[-1], 'Experiment Time',  # 28-31
                'Stand years', '',  # 32-33
                *calc_params[0:22],
                *irra_params[26:28],  # Cl36/38 productivities ratio
                *smp_params[4:13],  # standard samples name, age, ...
                *smp_params[0:4],  # J, sJ, MDF, sMDF
                *calc_params[22:48],
                *smp_params[13:16],  # fitting method, convergence, iteration
                ['Linear', 'Exponential', 'Power'][smp_params[16:19].index(True)],
                *smp_params[19:32],
                'Auto Plateau Method',  #
            ]] * len(interceptData))
        sample.TotalParam[31] = ["-".join(re.findall("(.*)-(.*)-(.*)T(.*):(.*):(.*)", item)[0]) for item in experimentTime]
        np = len(sample.SequenceName)
        stand_time_second = [
            calc_funcs.get_datetime(*sample.TotalParam[31][i].split('-')) - calc_funcs.get_datetime(*sample.TotalParam[30][i].split('-')) for i in range(np)]
        sample.TotalParam[32] = [i / (3600 * 24 * 365.242) for i in stand_time_second]  # stand year

        sample.UnselectedSequence = list(range(np))
        sample.SelectedSequence1 = []
        sample.SelectedSequence2 = []
        smp_funcs.recalculate(sample, *[True]*12)  # Calculation after submitting row data
        smp_funcs.update_table_data(sample)  # Update table after submittion row data and calculation
        # update cache
        cache_key = http_funcs.create_cache(sample)
        # write mysql
        http_funcs.set_mysql(request, models.CalcRecord, fingerprint, cache_key=cache_key)
        log_funcs.set_info_log(self.ip, '004', 'info', f'Success to submit raw file')
        return JsonResponse({})


class ParamsSettingView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = [
            "show_irra", "show_calc"
        ]

    def show_irra(self, request, *args, **kwargs):
        allIrraNames = list(models.IrraParams.objects.values_list('name', flat=True))
        log_funcs.set_info_log(self.ip, '005', 'info', f'Show irradiation param project names: {allIrraNames}')
        return render(request, 'irradiation_setting.html', {'allIrraNames': allIrraNames})

    def show_calc(self, request, *args, **kwargs):
        allCalcNames = list(models.CalcParams.objects.values_list('name', flat=True))
        log_funcs.set_info_log(self.ip, '005', 'info', f'Show calculation param project names: {allCalcNames}')
        return render(request, 'calculation_setting.html', {'allCalcNames': allCalcNames})

    def show_smp(self, request, *args, **kwargs):
        allSmpNames = list(models.SmpParams.objects.values_list('name', flat=True))
        log_funcs.set_info_log(self.ip, '005', 'info', f'Show sample param project names: {allSmpNames}')
        return render(request, 'sample_setting.html', {'allSmpNames': allSmpNames})

    def change_param_objects(self, request, *args, **kwargs):
        type = str(self.body['type'])  # type = irra, calc, smp
        model_name = f"{type.capitalize()}Params"
        try:
            name = self.body['name']
            param_file = getattr(models, model_name).objects.get(name=name).file_path
            param = file_funcs.read_setting_file(param_file)
            return JsonResponse({'status': 'success', 'param': param})
        except KeyError:
            sample = self.sample
            param = []
            data = basic_funcs.getTransposed(sample.TotalParam)[0]
            if 'irra' in type.lower():
                param = [*data[0:20], *data[56:58], *data[20:27], *basic_funcs.getIrradiationDatetimeByStr(data[27]), data[28], '', '']
            if 'calc' in type.lower():
                param = [*data[34:56], *data[71:97]]
            if 'smp' in type.lower():
                param = [*data[67:71], *data[58:67], *data[97:100], *basic_funcs.getMethodFittingLawByStr(data[100]), *data[101:114]]
            if not param:
                return JsonResponse({'status': 'fail', 'msg': 'no param project exists in database\n'})
            return JsonResponse({'status': 'success', 'param': param})
        except Exception as e:
            return JsonResponse({'status': 'fail', 'msg': 'no param project exists in database\n' + str(e)})

    def edit_param_object(self, request, *args, **kwargs):
        ip = http_funcs.get_ip(request)
        flag = str(self.body['flag']).lower()
        name = self.body['name']
        pin = self.body['pin']
        params = self.body['params']
        type = str(self.body['type'])  # type = irra, calc, smp
        model_name = f"{type.capitalize()}Params"
        model = getattr(models, model_name)
        if flag == 'create':
            email = self.body['email']
            if name == '' or pin == '':
                log_funcs.set_info_log(
                    self.ip, '005', 'info', f'Fail to create {type.lower()} project, empty name or pin')
                return JsonResponse({'status': 'fail', 'msg': 'empty name or pin'})
            elif model.objects.filter(name=name).exists():
                log_funcs.set_info_log(
                    self.ip, '005', 'info', f'Fail to create {type.lower()} project, duplicate name, name: {name}')
                return JsonResponse({'status': 'fail', 'msg': 'duplicate name'})
            else:
                path = file_funcs.save_setting_file(settings.SETTINGS_ROOT, name, type, params)
                model.objects.create(name=name, pin=pin, file_path=path, uploader_email=email, ip=ip)
                log_funcs.set_info_log(
                    self.ip, '005', 'info',
                    f'Success to create {type.lower()} project, '
                    f'name: {name}, email: {email}, file path: {path}')
                return JsonResponse({'status': 'success'})
        else:
            try:
                old = model.objects.get(name=name)
            except Exception:
                log_funcs.set_info_log(
                    self.ip, '005', 'info',
                    f'Fail to change selected {type.lower()} project, '
                    f'it does not exist in the server, name: {name}')
                return JsonResponse({'status': 'fail', 'msg': 'current project does not exist'})
            if pin == old.pin:
                if flag == 'update':
                    path = file_funcs.update_setting_file(old.file_path, params)
                    old.save()
                    log_funcs.set_info_log(
                        self.ip, '005', 'info',
                        f'Success to update the {type.lower()} project, name: {name}, path: {path}')
                    return JsonResponse({'status': 'success'})
                elif flag == 'delete':
                    if file_funcs.delete_setting_file(old.file_path):
                        old.delete()
                        log_funcs.set_info_log(
                            self.ip, '005', 'info',
                            f'Success to delete the {type.lower()} project does been deleted, name: {name}')
                        return JsonResponse({'status': 'success'})
                    else:
                        log_funcs.set_info_log(
                            self.ip, '005', 'info',
                            f'Fail to delete {type.lower()} projects, '
                            f'something wrong happened, name: {name}')
                        return JsonResponse({'status': 'fail', 'mas': 'something wrong happened when delete params'})
            else:
                return JsonResponse({'status': 'fail', 'msg': 'wrong pin'})


def open_last_object(request):
    fingerprint = request.POST.get('fingerprint')
    # print(cache.keys('*'))
    try:
        last_record = models.CalcRecord.objects.filter(user=str(fingerprint)).order_by('-id')[0]
        cache_key = last_record.cache_key
        sample = pickle.loads(cache.get(cache_key))
        # sample = basic_funcs.getJsonLoads(cache.get(cache_key))
        if sample is None:
            raise IndexError
    except (BaseException, Exception):
        # print('No file found in cache!')
        sample = samples.Sample()
        smp_funcs.initial(sample)
        return http_funcs.open_object_file(request, sample, web_file_path='')
    else:
        return http_funcs.open_object_file(request, sample, web_file_path='', cache_key=cache_key)
