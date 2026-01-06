#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2025 Yang 
# webarar - ws_funcs
# ==========================================
#
#
# 
"""
import time
import copy
import traceback
import numpy as np
import pandas as pd
import json
from channels.generic.websocket import WebsocketConsumer
from . import ap, basic_funcs


# 存储 WebSocket 连接（key: task_id, value: consumer实例）
active_connections = {}
task_ready_events = {}


class ProgressConsumer(WebsocketConsumer):
    def connect(self):
        # 获取URL中的task_id
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.last = 0
        self.next = 100
        self.index = 1
        # 接受WebSocket连接
        self.accept()
        # 将当前连接存入全局字典，供任务线程调用
        active_connections[self.task_id] = self

        # 触发就绪事件（唤醒子线程）
        if self.task_id in task_ready_events:
            ready_event = task_ready_events[self.task_id]
            ready_event.set()

    def disconnect(self, close_code):
        # 连接关闭时，从字典中移除
        if self.task_id in active_connections:
            del active_connections[self.task_id]

    # 自定义方法 示例：向前端推送进度
    def send_message(self, **kwargs):
        self.last = kwargs.get('progress', self.last)
        self.next = kwargs.pop('next', self.next)
        self.index = kwargs.get('index', self.index)
        try:
            self.send(text_data=ap.smp.json.dumps({**kwargs, }))
        except TypeError as e:
            self.send(text_data=json.dumps({'error': f'TypeError: {str(e)}', 'close': True}))


def check_ws_connection(task_id) -> bool:
    if task_id not in task_ready_events:
        raise ConnectionError(f"WebSocket connection failed.")
    ready_event = task_ready_events[task_id]
    # 等待连接建立
    if not ready_event.wait(timeout=15):
        if task_id in task_ready_events:
            del task_ready_events[task_id]
        raise TimeoutError(f"WebSocket connection timeout.")
    # 检测连接是否存在
    if task_id not in active_connections:
        if task_id in task_ready_events:
            del task_ready_events[task_id]
        raise ConnectionError(f"WebSocket connection not found.")
    return True


def raw_regression(cls, task_id, file_names, file_paths, filter_names, filter_paths):
    check_ws_connection(task_id)
    num_files = len(file_paths)
    raws = []
    try:
        for index in range(num_files):
            if task_id in active_connections:
                progress = int((index + 1) / num_files * 10)
                active_connections[task_id].send_message(
                    progress=progress, finished=False, info=f"Reading file #{index + 1}: {file_names[index]}")
            raws.append(ap.smp.raw.to_raw(file_paths[index], filter_paths[index], file_names[index]))

        raw = ap.smp.raw.concatenate(raws)

        if not all([str(name).lower() == "seq" for name in filter_names]):
            sequence_index = None
            isotopic_index = None
            total_num = raw.sequence_num * 5 * 5

            def power(a0, a1):
                raise ValueError("Deprecated regression")

            handlers = [ap.calc.regression.linest, ap.calc.regression.quadratic, ap.calc.regression.exponential,
                        power, ap.calc.regression.average]
            for j, sequence in enumerate(raw.get_sequence(index=None, flag=None)):
                if hasattr(sequence_index, '__getitem__') and sequence.index not in sequence_index:
                    continue
                isotope: pd.DataFrame = sequence.get_data_df()
                selected: pd.DataFrame = isotope[sequence.get_flag_df()[list(range(1, 11))]]
                selected: list = [
                    selected[[isotopic_index * 2 + 1, 2 * (isotopic_index + 1)]].dropna().values.tolist()
                    for isotopic_index in list(range(5))]
                for index, isotopic_data in enumerate(selected):
                    if hasattr(isotopic_index, '__getitem__') and index not in isotopic_index:
                        continue
                    linesResults, regCoeffs = [], []
                    for h, handler in enumerate(handlers):
                        line_data, line_results, reg_coeffs = \
                            ap.calc.raw_funcs.get_regression_results(isotopic_data, handler)
                        linesResults.append(line_results)
                        regCoeffs.append(reg_coeffs)
                        if task_id in active_connections:
                            progress = int((j * 5 * 5 + index * 5 + h + 1) / total_num * 90 + 10)
                            active_connections[task_id].send_message(
                                progress=progress, finished=False,
                                info=f"Sequence: {j}, Isotope: {index}, Regression: {handler.__name__}")
                    try:
                        sequence.results[index] = linesResults
                        sequence.coefficients[index] = regCoeffs
                    except IndexError:
                        sequence.results.insert(index, linesResults)
                        sequence.coefficients.insert(index, regCoeffs)
                    except TypeError:
                        sequence.results = [linesResults]
                        sequence.coefficients = [regCoeffs]

        # update cache
        cache_key = basic_funcs.set_cache(raw, user_id=cls.user_id)
        if task_id in active_connections:
            active_connections[task_id].send_message(
                progress=100, finished=True, raw_cache_key=cache_key, info="Completed! Redirecting...")
            del active_connections[task_id]

    except Exception as e:
        if task_id in active_connections:
            active_connections[task_id].send_message(progress=0, finished=True, error=str(e))
            del active_connections[task_id]

    pass


def recalculate(cls, task_id):
    check_ws_connection(task_id)
    sample: ap.Sample = cls.sample
    checked_options = cls.content['checked_options']
    others = cls.content.pop('others', {})
    isochron_mark = cls.content.pop('isochron_mark', False)

    if isochron_mark:
        sample.IsochronMark = isochron_mark.copy()
        sample.sequence()
    # backup for later comparision
    components_backup = copy.deepcopy(ap.smp.basic.get_components(sample))

    progress = 1
    try:
        # Re-calculating based on selected options
        params = {
            're_initial': False,
            're_corr_blank': False,
            're_corr_massdiscr': False,
            're_corr_decay': False,
            're_degas_ca': False,
            're_degas_k': False,
            're_degas_cl': False,
            're_degas_atm': False,
            're_degas_r': False,
            're_calc_ratio': False,
            're_calc_apparent_age': False,
            're_plot': False,
            're_plot_style': False,
            're_set_table': False,
            're_table_style': False
        }
        params = dict(zip(params.keys(), checked_options))
        n = checked_options.count(True)
        cc = 0
        active_connections[task_id].send_message(progress=1, next=round(100/n), finished=False, info=f"Start")
        for index, (key, val) in enumerate(params.items()):
            if not val:
                continue
            cc += 1
            progress = round(cc / n * 100)
            next = round((cc + 1) / n * 100)
            try:
                # sample.recalculate(**{key: val}, **others)
                sample_recalculate(
                    sample=sample, ws=active_connections[task_id], next=next, index=index,
                    **{key: val}, **others
                )
            except ap.smp.basic.ParamsInvalid as e:
                print(traceback.format_exc())
                active_connections[task_id].send_message(
                    progress=progress, close=True, finished=progress == 100, next=next,
                    error=f"{type(e).__name__}: {e}", index=index, error_context=e.context)
                return
            except (Exception, BaseException) as e:
                print(traceback.format_exc())
                active_connections[task_id].send_message(
                    progress=progress, close=True, finished=progress == 100, next=next,
                    error=f"{type(e).__name__}: {e}", index=index)
                return
            else:
                active_connections[task_id].send_message(
                    progress=progress, finished=False, info=f"Completed: {key}", index=index, next=next,
                )

    except Exception as e:
        print(traceback.format_exc())
        if task_id in active_connections:
            active_connections[task_id].send_message(progress=progress, close=True, finished=True, error=str(e))
            del active_connections[task_id]
    ap.smp.table.update_table_data(sample)  # Update data of tables after re-calculation

    # update cache
    basic_funcs.set_cache(sample, key=cls._cache_key)
    res = ap.smp.basic.get_diff_smp(backup=components_backup, smp=ap.smp.basic.get_components(sample))

    # finished
    if task_id in active_connections:
        active_connections[task_id].send_message(
            progress=100, finished=True, info="Recalculation completed! ", res=res)
        del active_connections[task_id]


def click_chart(cls, task_id):
    check_ws_connection(task_id)
    sample: ap.Sample = cls.sample
    clicked_index = cls.content['clicked_index']
    current_set = cls.content['current_set']
    auto_replot = cls.content['auto_replot']
    figures = cls.content['figures']
    all_figures = ['figure_1', 'figure_2', 'figure_3', 'figure_4', 'figure_5', 'figure_6', 'figure_7']

    if not np.iterable(clicked_index):
        active_connections[task_id].send_message(
            progress=0, close=True, finished=True, refresh=False,
            error=f"{TypeError.__name__}: Clicked index is not iterable. {clicked_index = }. Changes are not applied.")
        return

    components_backup = copy.deepcopy(ap.smp.basic.get_components(sample))

    for idx in clicked_index:
        sample.set_selection(int(idx), int(current_set))

    # update tables
    ap.smp.table.update_table_data(sample)
    res = ap.smp.basic.get_diff_smp(backup=components_backup, smp=ap.smp.basic.get_components(sample))
    if task_id in active_connections:
        active_connections[task_id].send_message(
            progress=1, finished=False, close=False, res=res, refresh=True, info="All tables have been updated!",
        )

    def get_res(figure: str, progress: int, refresh: bool = False):
        components_backup = copy.deepcopy(ap.smp.basic.get_components(sample))
        if figure not in all_figures:
            raise KeyError
        try:
            sample.recalculate(re_plot=True, isInit=False, isIsochron=True,
                               isPlateau=figure == "figure_1", figures=[figure])
        except ap.smp.basic.ParamsInvalid as e:
            print(traceback.format_exc())
            active_connections[task_id].send_message(
                progress=progress, close=True, finished=False,
                error=f"{type(e).__name__}: {e}. Changes are not applied.", refresh=refresh, error_context={})
            return
        except (Exception, BaseException) as e:
            print(traceback.format_exc())
            active_connections[task_id].send_message(
                progress=progress, close=True, finished=False,
                error=f"{type(e).__name__}: {e}. Changes are not applied.", refresh=refresh, error_context={})
            return
        else:
            # only the current figure was changed
            res = ap.smp.basic.get_diff_smp(
                backup=components_backup, smp=ap.smp.basic.get_components(sample))
            if task_id in active_connections:
                active_connections[task_id].send_message(
                    progress=progress, finished=False, refresh=refresh,
                    info=f"{figure.upper()} was updated.", res=res
                )

    if auto_replot:
        cc = 0
        total = len(all_figures)
        for each in figures:
            cc += 1
            get_res(each, progress=round(cc / total * 100), refresh=True)
        for each in all_figures:
            if each in figures:
                continue
            cc += 1
            get_res(each, progress=round(cc / total * 100),)

    basic_funcs.set_cache(sample, cls._cache_key)  # 更新缓存

    # finished
    if task_id in active_connections:
        active_connections[task_id].send_message(
            progress=100, finished=True, info="All figures have been updated!", res={}, refresh=False)
        del active_connections[task_id]


def sample_recalculate(
        sample: ap.Sample, re_initial: bool = False,
        re_corr_blank: bool = False, re_corr_massdiscr: bool = False,
        re_corr_decay: bool = False, re_degas_ca: bool = False, re_degas_k: bool = False,
        re_degas_cl: bool = False, re_degas_atm: bool = False, re_degas_r: bool = False,
        re_calc_ratio: bool = False, re_calc_apparent_age: bool = False,
        re_plot: bool = False, re_plot_style: bool = False, re_set_table: bool = False,
        re_table_style: bool = False, ws: ProgressConsumer = None, next: int = 0, index: int = 0, **kwargs
):
    if len(sample.UnselectedSequence) == len(sample.SelectedSequence1) == len(sample.SelectedSequence2) == 0:
        sample.UnselectedSequence = list(range(len(sample.SequenceName)))

    # --- initializing ---
    if re_initial:  # 1
        ap.smp.initial.re_set_smp(sample)
    # --- calculating ---
    if re_corr_blank:  # 2
        ap.smp.corr.corr_blank(sample)
    if re_corr_massdiscr:  # 3
        ap.smp.corr.corr_massdiscr(sample)
    if re_corr_decay:  # 4
        ap.smp.corr.corr_decay(sample)
    if re_degas_ca:  # 5
        ap.smp.corr.calc_degas_ca(sample)
    if re_degas_k:  # 6
        ap.smp.corr.calc_degas_k(sample)
    if re_degas_cl:  # 7
        ap.smp.corr.calc_degas_cl(sample)
    if re_degas_atm:  # 8
        ap.smp.corr.calc_degas_atm(sample)
    if re_degas_r:  # 9
        ap.smp.corr.calc_degas_r(sample)
        ap.smp.corr.calc_degas_c(sample)
    if re_calc_ratio:  # 10
        ap.smp.corr.calc_ratio(sample)
        monte_carlo = sample.TotalParam[112][0]
        if monte_carlo and sample.Info.sample.type != "Air":
            ws.send_message(
                progress=ws.last, finished=False, info=f"Start Monte-Carlo Simulation", index=index, next=ws.next,
            )
            res = ap.smp.corr.monte_carlo_f(sample=sample)
            #
            list_res = []
            cc = 0; total = sample.Info.experiment.step_num
            start = ws.last
            step = (ws.next - ws.last) / total
            for each_step in res:
                cc += 1
                ws.send_message(
                    progress=round(start + cc * step), finished=False,
                    info=f"Monte Carlo simulating: {cc}/{total}", index=index
                )
                list_res.append(each_step)

            res = np.array(list_res).T  # res is a generator for [*F, *age, iso, ...]
            sample.ApparentAgeValues[0:2] = res[0:2]
            sample.ApparentAgeValues[2] = [np.nan] * sample.Info.experiment.step_num
            sample.ApparentAgeValues[3] = [np.nan] * sample.Info.experiment.step_num
            sample.ApparentAgeValues[4] = [np.nan] * sample.Info.experiment.step_num
            sample.ApparentAgeValues[5] = [np.nan] * sample.Info.experiment.step_num
            # degas
            sample.DegasValues = res[2:2 + 32]
            # isochron data
            sample.IsochronValues = res[2 + 32:2 + 32 + 39]
            # corrected
            sample.CorrectedValues = res[2 + 32 + 39:2 + 32 + 39 + 10]
            # publish
            sample.PublishValues[0] = copy.deepcopy(sample.DegasValues[0])
            sample.PublishValues[1] = copy.deepcopy(sample.DegasValues[8])
            sample.PublishValues[2] = copy.deepcopy(sample.DegasValues[10])
            sample.PublishValues[3] = copy.deepcopy(sample.DegasValues[20])
            sample.PublishValues[4] = copy.deepcopy(sample.DegasValues[24])
            sample.PublishValues[5:7] = copy.deepcopy(sample.ApparentAgeValues[2:4])
            sample.PublishValues[7:9] = copy.deepcopy(sample.ApparentAgeValues[6:8])

        else:
            ws.send_message(
                progress=ws.next, finished=False, info=f"Completed: re_calc_ratio", index=index, next=next,
            )

    if re_calc_apparent_age:  # 11
        ap.smp.basic.calc_apparent_ages(sample)
    # --- plot and table ---
    if re_plot:  # 12
        ap.smp.plots.set_plot_data(sample, **kwargs)
    if re_plot_style:  # 13
        ap.smp.style.set_plot_style(sample)
    if re_set_table:  # 14
        ap.smp.table.update_table_data(sample)
    if re_table_style:  # 15
        ap.smp.style.set_table_style(sample)
    return sample

