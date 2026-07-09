#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2025 Yang 
# webarar - thermo_views
# ==========================================
#
#
# 
"""
import os
import traceback
import numpy as np
import time
import itertools

from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache

from . import models
from programs import http_funcs, ap
from programs.log_funcs import debug_print


class ThermoView(http_funcs.ArArView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = []

    # /calc/thermo
    def get(self, request, *args, **kwargs):
        # names = list(models.IrraParams.objects.values_list('name', flat=True))
        # log_funcs.set_info_log(self.ip, 'info', f'Show irradiation param project names: {names}')
        allThermoNames = list(models.ThermoParams.objects.values_list('name', flat=True))
        allExportPDFNames = list(models.ExportPdfParams.objects.values_list('name', flat=True))
        return self.render(request, 'thermo.html', {'allThermoNames': allThermoNames, 'allExportPDFNames': allExportPDFNames})

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
                web_file_path, file_name, suffix = http_funcs.upload(file, destination_folder, request=request)
                arr_file = os.path.basename(web_file_path)
            except (Exception, BaseException) as e:
                pass
            else:
                if str(suffix).lower() == ".arr":
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
            self.error_msg = f"Random index is empty, or the path '{loc}' does not exist."
            messages.error(request, self.error_msg)
            return self.JsonResponse({'msg': self.error_msg}, status=403)

        if arr_file_name == "":
            for root, dirs, files in os.walk(loc):
                for file in files:
                    if file.endswith('.arr'):
                        arr_file_name = file
                        name = arr_file_name.strip('.arr')

        arr_file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
        while not (os.path.isfile(arr_file_path) and os.path.exists(arr_file_path)):
            random_index = os.path.dirname(random_index)
            arr_file_path = os.path.join(settings.MDD_ROOT, f"{random_index}\\{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
            if random_index == os.path.dirname(random_index):
                raise FileNotFoundError

        sample = ap.from_arr(file_path=arr_file_path)
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
            ar = np.array(ar)
            sar = np.array(sar)
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
            elif str(logdr2_method).lower().startswith('cylinder'.lower()):
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_cylinder(f, ti, ar=ar, sar=sar, ln=use_ln)
            elif str(logdr2_method).lower().startswith('cube'.lower()):
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_cube(f, ti, ar=ar, sar=sar, ln=use_ln)
            else:
                raise KeyError(f"Geometric model not found: {str(logdr2_method).lower()}")
        except (Exception, BaseException) as e:
            self.error_msg = f"The D/r2 calculation failed. {type(e).__name__}: {str(e)}"
            messages.error(request, self.error_msg)
            return self.JsonResponse({'msg': self.error_msg}, status=403)

        data = np.array([
            sequence.value, te, ti, age, sage, ar, sar, f, dr2, ln_dr2, wt
        ], dtype=np.float64).tolist()
        data.insert(0, (np.where(np.array(data[3]) > 0, True, False) & np.isfinite(data[3])).tolist())
        data.insert(1, [1 for i in range(nsteps)])

        res = False
        mch_out = os.path.join(loc, f'{name}_mch-out.dat')
        mages_out = os.path.join(loc, f'{name}_mages-out.dat')
        ages_sd = os.path.join(loc, f'{name}_ages-sd.samp')
        if os.path.isfile(mch_out) and os.path.isfile(mages_out) and os.path.isfile(ages_sd):
            res = True

        file_IN = open(os.path.join(loc, f"{name}.IN"), "w")
        for i in range(nsteps):
            if f[i] >= 1:
                f[i] = 0.9999999999
            # step_num, T_°C, t_min, 39Ar, %s, Cum39Ar, Age(Ma), s, Ts?, Cl_age?, s
            file_IN.writelines(f"{i+1},{te[i]},{ti[i]},{ar[i]},{sar[i]/ar[i]*100},{f[i]*100},{age[i]},{sage[i]},{0},{age[i]},{sage[i]}\n")
        file_IN.close()

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


        arr_file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
        while not (os.path.isfile(arr_file_path) and os.path.exists(arr_file_path)):
            random_index = os.path.dirname(random_index)
            arr_file_path = os.path.join(settings.MDD_ROOT, f"{random_index}\\{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
            if random_index == os.path.dirname(random_index):
                raise FileNotFoundError
        sample = ap.from_arr(file_path=arr_file_path)

        arr = ap.smp.diffusion_funcs.DiffArrmultiFunc(smp=sample, loc=loc, name=sample_name)

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
        arr.dr2, arr.xlogd, arr.wt = filtered_data[10:13]

        arr.f.insert(0, 0)
        arr.f = np.where(np.array(arr.f) >= 1, 0.9999999999999999, np.array(arr.f))
        arr.max_temp = 1100 + 273
        arr.ngauss = int(params[1])
        arr.ndom = int(params[0])


        file_IN = open(os.path.join(loc, f"{sample_name} - Arrmulti.IN"), "w")
        for i in range(arr.ni):
            # step_num, T_°C, t_min, 39Ar, %s, Cum39Ar, Age(Ma), s, Ts?, Cl_age?, s
            file_IN.writelines(
                f"{i + 1},{filtered_data[3][i]},{filtered_data[4][i]},{filtered_data[7][i]},{filtered_data[8][i] / filtered_data[7][i] * 100},{filtered_data[9][i] * 100},{filtered_data[5][i]},{filtered_data[6][i]},{0},{filtered_data[5][i]},{filtered_data[6][i]}\n")
        file_IN.close()


        arr.main()

        # return self.JsonResponse({})
        return self.run_agemon(self, request, *args, **kwargs)

    def run_agemon(self, request, *args, **kwargs):
        sample_name = self.body['sample_name']
        arr_file_name = self.body['arr_file_name']
        random_index = self.body['random_index']
        max_age = self.body['max_age']
        data = self.body['data']
        loc = os.path.join(settings.MDD_ROOT, random_index)
        if not os.path.exists(loc) or random_index == "":
            return self.JsonResponse({}, status=403)

        arr_file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
        print(f"{arr_file_path = }")
        while not (os.path.isfile(arr_file_path) and os.path.exists(arr_file_path)):
            random_index = os.path.dirname(random_index)
            arr_file_path = os.path.join(settings.MDD_ROOT, f"{random_index}\\{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
            if random_index == os.path.dirname(random_index):
                raise FileNotFoundError

        sample = ap.from_arr(file_path=arr_file_path)
        sample.name(sample_name)

        print(f"{sample.name() = }")

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

        loc = os.path.join(settings.MDD_ROOT, f'{random_index}')
        if not os.path.exists(loc) or random_index == "":
            return self.JsonResponse({"random_index": random_index}, status=403)
        arr_file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
        while not (os.path.isfile(arr_file_path) and os.path.exists(arr_file_path)):
            random_index = os.path.dirname(random_index)
            arr_file_path = os.path.join(settings.MDD_ROOT, f"{random_index}\\{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
            if random_index == os.path.dirname(random_index):
                raise FileNotFoundError

        smp = ap.from_arr(arr_file_path)
        ti = np.array(smp.TotalParam[123], dtype=np.float64).round(2)  # time in second
        temps = np.array(smp.TotalParam[124], dtype=np.float64)  # temperature in Celsius
        if params[10] == "40":
            # ar = np.array(smp.DegasValues[24], dtype=np.float64)  # Ar40r
            return self.run_40ar_walker(request, args, kwargs)
        elif params[10] == "39":
            ar = np.array(smp.DegasValues[20], dtype=np.float64)  # Ar39K
        else:
            self.error_msg = f"{params[10] = }, is not 40 or 39"
            messages.error(request, self.error_msg)
            return self.JsonResponse({'msg': self.error_msg}, status=403)
        targets = ar.cumsum() / sum(ar)

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

        if checkable_params[9]:  # searching for nearby places
            energies_list = []
            fractions_list = []
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
                    atom_density=ad, frequency=f, simulation=False, targets=targets, epsilon=0.05,
                    use_walker1=use_walker1
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
        print(f"run ar40 walker, {loc = }")
        if not os.path.exists(loc) or random_index == "":
            return self.JsonResponse({"random_index": random_index}, status=403)
        arr_file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
        while not (os.path.isfile(arr_file_path) and os.path.exists(arr_file_path)):
            random_index = os.path.dirname(random_index)
            arr_file_path = os.path.join(settings.MDD_ROOT, f"{random_index}\\{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
            if random_index == os.path.dirname(random_index):
                raise FileNotFoundError
        smp = ap.from_arr(arr_file_path)

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
        # parent = 100000000  # parent 40K
        f = domain_params[20]  # frequency
        pumping = domain_params[21]
        # ad = 1e10  # atom density
        # f = 1e13
        dimension = 3

        def _thermal_log(ti):
            log = [[30, 23, 16, 7, 3, 0], [20, 175, 190, 275, 600, 900]]
            upper = [log[0][0], log[1][0]]
            for i in range(len(log[0])):
                if ti >= log[0][i]:
                    if upper[0] == log[0][i]:
                        return upper[1]
                    else:
                        return (upper[1] - log[1][i]) / (upper[0] - log[0][i]) * (ti - log[0][i]) + log[1][i]
                else:
                    upper = [log[0][i], log[1][i]]
            raise ValueError

        age = 30  # in Ma
        scale = 0.5  # in Ma
        dt = 10000 * 3600 * 24 * 365.2425   # to seconds
        ti = np.ones(int(age / scale)) * scale
        times = np.cumsum(ti)  # cumulative time
        temps = [_thermal_log(i) for i in times]
        debug_print('thermal history', list(zip(temps, times)))
        times = times * 3600 * 24 * 365.2425 * 1000000  # to seconds
        # temps = np.ones(int(age / scale)) * 10
        # temps[:5] = 400
        # temps[5:10] = 400
        # temps[10:20] = 350
        # temps[20:30] = 300
        # temps[30:40] = 250
        # temps[40:50] = 200
        # temps[50:70] = 150
        # temps[70:100] = 25
        # temps[100:] = 10

        statuses = [True for i in range(len(ti))]
        targets = [0 for i in range(len(ti))]
        e_combinations = [energies[: ndoms]] * 10
        f_combinations = [fractions[: ndoms]] * 10

        init_fs_list = [
            [1, 0.99, 0.85, 0.8, 0.6, 0.5],
            [1, 0.99, 0.85, 0.8, 0.6, 0.5],
            [1, 0.99, 0.85, 0.8, 0.6, 0.5],
            [1, 0.99, 0.85, 0.8, 0.6, 0.5],
            [1, 0.99, 0.85, 0.8, 0.6, 0.5],
            [1, 0.99, 0.85, 0.8, 0.6, 0.5],
            [1, 0.99, 0.85, 0.8, 0.6, 0.5],
            [1, 0.99, 0.85, 0.8, 0.6, 0.5],
            [1, 0.99, 0.85, 0.8, 0.6, 0.5],
            [1, 0.99, 0.85, 0.8, 0.6, 0.5],
        ]
        init_ds_list = [
            [5e11, 2e10, 6e11, 1e10, 1e10, 1e11],
            [5e11, 2e10, 6e11, 1e10, 1e10, 1e11],
            [5e11, 2e10, 6e11, 1e10, 1e10, 1e11],
            [5e11, 3e10, 6e11, 1e10, 1e10, 1e11],
            [5e11, 3e10, 6e11, 1e10, 1e10, 1e11],
            [5e11, 3e10, 6e11, 1e10, 1e10, 1e11],
            [5e11, 4e10, 6e11, 1e10, 1e10, 1e11],
            [5e11, 4e10, 6e11, 1e10, 1e10, 1e11],
            [5e11, 4e10, 6e11, 1e10, 1e10, 1e11],
            [5e11, 4e10, 6e11, 1e10, 1e10, 1e11],
        ]

        debug_print(f"Run 40Ar {use_walker1 = }, {scale = }, {gs = }, {ad = }, {f = }")

        for index, (_e, _f) in enumerate(list(itertools.product(*[e_combinations, f_combinations]))):
            debug_print(f"{index = }, {_e = }, {_f = }")

            try:

                ## 先模拟热史

                do_history_simulating = True
                # do_history_simulating = False

                if do_history_simulating:

                    file_name = f"History {'walker1' if use_walker1 else 'walker2'} k={scale:.1f}a " \
                                f"es={'-'.join([str(int(i / 1000)) for i in _e])} " \
                                f"fs={'-'.join([str(i) for i in _f])} " \
                                f"{dt=:.0f} " \
                                f"{parent=:.0f} " \
                                f"{gs=:.0f} " \
                                f"{ad=:.0e} " \
                                f"{f=:.0e} " \
                                f"{ndoms=:.0f} " \
                                # f"temp={set(temps)} "

                    _start = time.time()
                    demo, status = ap.thermo.arw.run(
                        times, temps, statuses,
                        _e, _f, ndoms, file_name=file_name, k=dt, grain_szie=gs, dimension=dimension,
                        atom_density=ad, frequency=f, simulation=False, targets=targets, epsilon=0.05,
                        use_walker1=use_walker1, decay=5.53e-10, parent=parent
                    )
                    ap.thermo.arw.save_ads(demo, f"{loc}", name=demo.name + f" {(time.time() - _start) / 3600:.2f}h")

                    init_fs = []
                    init_ds = []

                else:
                    # filename = f"walker2 k=10000.0a es=135-126-152 fs=1-0.97-0.74 dt=3155695200000 parent=800000000 gs=275 ad=0e+00 f=1e+13 ndoms=3 pumping=True multi 1.35h.ads"
                    # filename = "walker2 k=3000.0a es=135-126-152 fs=1-0.97-0.74 dt=3155695200000 parent=800000000 gs=275 ad=0e+00 f=1e+13 ndoms=3 temp={200.0, 10.0, 300.0, 400.0, 150.0, 25.0, 250.0, 350.0} pumping=True multi 4.99h.ads"
                    # filename = "walker2 k=1000.0a es=135-126-152 fs=1-0.97-0.74 dt=3155695200000 parent=800000000 gs=275 ad=0e+00 f=1e+13 ndoms=3 pumping=False multi 12.27h.ads"
                    # filename = os.path.join(loc, filename)
                    # demo = ap.thermo.arw.read_ads(filename)

                    init_fs = init_fs_list[index]
                    init_ds = init_ds_list[index]
                    demo = ap.thermo.arw.demo_init(len(init_fs), [0] * len(init_fs), init_fs, 3, gs, init_ds, f, ss=1)

            except ap.thermo.arw.OverEpsilonError as e:
                debug_print(traceback.format_exc())
                return self.JsonResponse({})
            else:

                ## 再模拟实验过程

                # use_walker1 = False

                init_ds_str = ", ".join([f"{i:.0e}" for i in init_ds])

                file_name = f"{'walker1' if use_walker1 else 'walker2'} {k=:.1f} " \
                            f"{init_fs=}" \
                            f"init_ds=[{init_ds_str}] " \
                            f"es={'-'.join([str(int(i / 1000)) for i in _e])} " \
                            f"fs={'-'.join([str(i) for i in _f])} " \
                            f"{dt=:.0e} " \
                            f"{gs=:.0e} " \
                            f"{ad=:.0e} " \
                            f"{f=:.0e} " \
                            f"{ndoms=} " \
                            f"pumping={checkable_params[6]} " \
                            f"multi"

                debug_print(f"{file_name = }")

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

                debug_print('heating experiment', list(zip(temps, times)))

                try:
                    _start = time.time()
                    demo, status = ap.thermo.arw.run(
                        times, temps, statuses, _e, _f, ndoms, file_name=file_name, k=k, grain_szie=gs,
                        dimension=dimension, atom_density=0, frequency=f, simulation=False, targets=targets, epsilon=0.05,
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
            self.error_msg = f"Random index is empty, or the path '{loc}' does not exist."
            messages.error(request, self.error_msg)
            return self.JsonResponse({'msg': self.error_msg}, status=403)

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
                            k1 = k1 / (radius * 0.0001) ** 2  # μm to cm
                        # Closure temperature
                        k2 = -10 * m * ap.thermo.basic.GAS_CONSTANT * np.log(base)  # activation energy, kJ
                        try:
                            # Closure temperature
                            k3, _ = ap.thermo.basic.get_tc(da2=k1, sda2=0, E=k2 * 1000, sE=0, pho=0,
                                                           cooling_rate=cooling_rate, A=A)
                        except ValueError as e:
                            # print(e.args)
                            k3 = 999
                        return k1, k2/4.184, k3  # da2, E, Tc

                    try:
                        # Arrhenius line regression
                        # each_line[0:6] = ap.thermo.basic.fit(x, y, wtx, wty)  # intercept, slop, sa, sb, chi2, q
                        # b (intercept), sb, a (slope), sa, mswd, dF, Di, k, r2, chi_square, p_value, avg_err_s, cov
                        each_line[0:13] = ap.calc.regression.york2(x, wtx, y, wty, ri=np.zeros(len(x)))
                        each_line[1] = each_line[1] * 1  # 1 sigma
                        each_line[3] = each_line[3] * 1  # 1 sigma

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
                wtd_mean_ages.append(
                    [data[9][min(indexes) - 1] * 100 if min(indexes) != 0 else 0, data[9][max(indexes)] * 100,
                     *ap.calc.arr.wtd_mean(age, sage)])

        if plot_params[2]:  # cooling history
            if read_from_ins:
                # mdd_loc = r"C:\Users\Young\OneDrive\00-Projects\【2】个人项目\2024-06 MDD\MDDprograms\Sources Codes"
                mdd_loc = r"D:\DjangoProjects\webarar\private\mdd\MDDprograms\Sources Codes"
                arr = ap.smp.diffusion_funcs.DiffDraw(name="Y54", loc=mdd_loc, read_from_ins=read_from_ins)
            else:
                arr_file_path = os.path.join(loc, f"{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
                while not (os.path.isfile(arr_file_path) and os.path.exists(arr_file_path)):
                    random_index = os.path.dirname(random_index)
                    arr_file_path = os.path.join(settings.MDD_ROOT, f"{random_index}\\{arr_file_name}" + (".arr" if ".arr" not in arr_file_name else ""))
                    if random_index == os.path.dirname(random_index):
                        raise FileNotFoundError

                sample = ap.from_arr(file_path=arr_file_path)

                arr = ap.smp.diffusion_funcs.DiffDraw(smp=sample, loc=loc, name=sample_name)
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

        for i, [x, y1, y2] in enumerate(spectra_data[1]):
            print(f"{i = }, {min(x) = }, {max(x) = }, {min(y1) = }, {max(y1) = }, {min(y2) = }, {max(y2) = }")
        # print(spectra_data[2])

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
                released.append([i + 1, sum(ar[0:i + 1]) / sum(ar), *ads_released[i]])
        else:
            released.append([])
        spectra_data.append(released)
        release_name = '\n'.join(release_name)

        file_IN = open(os.path.join(loc, f"{sample_name} - Plot.IN"), "w")
        for i in range(n):
            # step_num, T_°C, t_min, 39Ar, %s, Cum39Ar, Age(Ma), s, Ts?, Cl_age?, s
            file_IN.writelines(
                f"{i + 1},{data[3][i]},{data[4][i]},{data[7][i]},{np.divide(data[8][i], data[7][i]) * 100},{data[9][i] * 100},{data[5][i]},{data[6][i]},{0},{data[5][i]},{data[6][i]}\n")
        file_IN.close()

        return self.JsonResponse({'status': 'success', 'data': ap.smp.json.dumps(spectra_data),
                                  'line_data': ap.smp.json.dumps(lines),
                                  'wtd_mean_ages': ap.smp.json.dumps(wtd_mean_ages),
                                  'release_name': release_name})

    def calculate_tc(self, request, *args, **kwargs):
        sample_name = self.body['sample_name']
        data = self.body['data']
        n = len(data)
        data = ap.calc.arr.transpose(data)

        main_color = ['white', 'green', '#397DA1', '#BA5624', '#BC3D85', '#3C6933', '#6C5D1E']
        middle_color = ['white', 'green', '#83CDFA', '#F1B595', '#E9CDE1', '#84B775', '#C0A737']
        shallow_color = ['white', 'green', '#E0F1FE', '#FBEBE3', '#CB73B0', '#B8F1A7', '#F9E16F']

        num = 10  # 5
        logdr2_methods = ['plane', 'cylinder', 'sphere']
        As = [8.7, 27, 55]
        radius = 100
        use_ln = True

        plot_data = {
            "data": [],
            "file_name": f"{sample_name}-Tc",
            "plot_names": [f"{sample_name}-Tc"],
        }

        for method_iondex in range(len(logdr2_methods)):

            logdr2_method = logdr2_methods[method_iondex]
            [_, _, seq_value, te, ti, age, sage, ar, sar, f, dr2, ln_dr2, wt] = data
            dr2, ln_dr2, wt = self.calculate_dr2(f, ti, ar, sar, use_ln=use_ln, logdr2_method=logdr2_method)
            te = [j + 273.15 for j in te]

            X, Y = 10000 / np.array(te), np.array(ln_dr2)

            line_width = 0.5

            plot_data['data'].append({
                'xAxis': [{
                    'extent': [4, 16], 'interval': [4, 8, 12, 16, 20, 24],
                    'title': f'10000 / T [10000/K]', 'nameLocation': 'middle',
                    'show_frame': True, 'label_size': 10, 'title_size': 10, 'line_width': line_width,
                }],
                'yAxis': [{
                    'extent': [-25, 0], 'interval': [-30, -25, -20, -15, -10, -5, 0],
                    'title': f'{"Ln(D/r2)" if use_ln else "Log(D/r2)"}', 'nameLocation': 'middle',
                    'show_frame': True, 'label_size': 10, 'title_size': 10, 'line_width': line_width,
                }],
                'series': [
                    {
                        'type': 'series.scatter', 'id': f'scatter_1', 'name': f'empty_scatters',
                        'fill_color': 'white', 'stroke_color': 'black', 'size': 2, 'line_width': line_width,
                        'data': np.transpose([X, Y]).tolist(),
                    },
                    {
                        'type': 'series.line', 'id': f'scatter_line', 'name': f'scatters_line',
                        'color': 'black',  'line_width': line_width,
                        'data': np.transpose([X, Y]).tolist(), 'line_caps': 'none',
                    },
                    {
                        'type': 'text', 'id': f'text_1', 'name': f'text', 'color': 'black', 'size': 10,
                        'data': [[10, -1]], 'line_width': line_width,
                        'text': f"Arrhenius plot - {logdr2_methods[method_iondex].capitalize()}",
                        'h_align': 'middle', 'v_align': 'top',
                    },
                ]
            })

            plot_data['data'].append({
                'xAxis': [{
                    'extent': [0, 100], 'interval': [0, 20, 40, 60, 80, 100],
                    'title': 'Cooling Rate [°C/Ma]', 'nameLocation': 'middle', 'show_frame': True,
                    'label_size': 10, 'title_size': 10, 'line_width': line_width,
                }],
                'yAxis': [{
                    'extent': [0, 850], 'interval': [0, 100, 200, 300, 400, 500, 600, 700, 800],
                    'title': 'Closure Temperature [°C]', 'nameLocation': 'middle', 'show_frame': True,
                    'label_size': 10, 'title_size': 10, 'line_width': line_width,
                }],
                'series': []
            })

            for tag in range(2, 8):

                index = []

                for row_index in range(len(data[1])):
                    if str(data[1][row_index]) == str(tag):
                        index.append(row_index)

                if len(index) == 0:
                    continue

                c1 = main_color[tag]
                c2 = middle_color[tag]
                c3 = shallow_color[tag]

                temp_range = [int(te[min(index)]-273.15), int(te[max(index)]-273.15)]

                print(f"name = {sample_name}, {index = }, logdr2_method = {logdr2_methods[method_iondex]}, {radius = }, {use_ln = }")
                A = As[method_iondex]
                each_line, X, Y, x, y, Tc_list = self._calculate_tc(
                    [_, _, seq_value, te, ti, age, sage, ar, sar, f, dr2, ln_dr2, wt],
                    logdr2_method, A, index=index, radius=radius, use_ln=use_ln, num=num)

                squared_r = each_line[8]
                [E, sE] = each_line[13:15]
                [da2, sda2] = each_line[15:17]
                [Tc, sTc] = each_line[17:19]

                plot_data['data'][-2]['series'].append({
                    'type': 'series.scatter', 'id': f'scatter_2', 'name': f'empty_scatters',
                    'fill_color': c2, 'stroke_color': c1, 'size': 2,  'line_width': line_width,
                    'data': np.transpose([x, y]).tolist(),
                })
                plot_data['data'][-2]['series'].append({
                    'type': 'series.line', 'id': f'line_1', 'name': f'regression_line',
                    'color': c1, 'z_index': 999, 'line_caps': 'none',  'line_width': line_width,
                    'data': np.transpose(
                        [[min(x), max(x)], [i * each_line[2] + each_line[0] for i in [min(x), max(x)]]]).tolist(),
                })
                plot_data['data'][-2]['series'].append({
                    'type': 'text', 'id': f'text_1', 'name': f'text', 'color': c1, 'size': 8,
                    'data': [[4.3, -14]], 'h_align': 'left', 'v_align': 'top', 'z_index': 999,
                    'text':
                        f'{int(temp_range[0])}~{int(temp_range[1])} °C<r>'
                        # f'intercept = {each_line[0]:.2f} ± {2 * each_line[1]:.2f}<r>'
                        # f'slope = {each_line[2]:.2f} ± {2 * each_line[3]:.2f}<r>'
                        # f'R2 = {squared_r:.4f}<r>'
                        f'E = {E / 4.184:.2f} ± {2 * sE / 4.184:.2f} kcal/mol<r>'
                        f'Tc = {Tc:.2f} ± {2 * sTc:.2f} °C<r>'
                        # f'D0/r2 = {da2 / 10 ** 6:.2f} ± {2 * sda2 / 10 ** 6:.2f} 106/a<r>'
                })

                # for i, s in enumerate(Tc_list[2]):
                #     plot_data['data'][-1]['series'].append({
                #         'type': 'series.line', 'id': f'error_line_{i}', 'name': f'error_line_{i}',
                #         'color': c3, 'line_caps': 'none',
                #         'data': np.transpose([[Tc_list[0][i], Tc_list[0][i]], [Tc_list[1][i]-2*s, Tc_list[1][i]+2*s]]).tolist(),
                #     })
                #     plot_data['data'][-1]['series'].append({
                #         'type': 'series.line', 'id': f'error_line_{i}', 'name': f'error_line_{i}',
                #         'color': c2, 'line_caps': 'none',
                #         'data': np.transpose([[Tc_list[0][i], Tc_list[0][i]], [Tc_list[1][i]-s, Tc_list[1][i]+s]]).tolist(),
                #     })
                #
                # plot_data['data'][-1]['series'].append({
                #     'type': 'series.line', 'id': f'tc_line', 'name': f'tc_line',
                #     'color': c1, 'line_caps': 'none',
                #     'data': np.transpose([Tc_list[0], Tc_list[1]]).tolist(),
                # })

                # plot_data['data'][-1]['series'].append({
                #     'type': 'text', 'id': f'text_1', 'name': f'text', 'color': c1, 'size': 8,
                #     'data': [[2, 160]], 'v_align': 'top', 'h_align': 'left', 'z_index': 999,
                #     'text': f'A = {A}<r>'
                #             f'Tc = {Tc_list[1][np.where(Tc_list[0] == 1)[0][0]]:.2f} ± {2 * Tc_list[2][np.where(Tc_list[0] == 1)[0][0]]:.2f} °C @ 1°C/Ma<r>'
                #             f'Tc = {Tc_list[1][np.where(Tc_list[0] == 10)[0][0]]:.2f} ± {2 * Tc_list[2][np.where(Tc_list[0] == 10)[0][0]]:.2f} °C @ 10°C/Ma<r>'
                #             f'Tc = {Tc_list[1][np.where(Tc_list[0] == 20)[0][0]]:.2f} ± {2 * Tc_list[2][np.where(Tc_list[0] == 20)[0][0]]:.2f} °C @ 20°C/Ma<r>'
                #             f'Tc = {Tc_list[1][np.where(Tc_list[0] == 100)[0][0]]:.2f} ± {2 * Tc_list[2][np.where(Tc_list[0] == 100)[0][0]]:.2f} °C @ 100°C/Ma',
                # })

            continue

        params_list = {
            "page_size": 'a4', "ppi": 72, "width": 9.5, "height": 7,
            "pt_width": 0.8, "pt_height": 0.8, "pt_left": 0.16, "pt_bottom": 0.18,
            "offset_top": 0, "offset_right": 0, "offset_bottom": 25, "offset_left": 35,
            "plot_together": False, "show_frame": True,
        }

        filename = f"{sample_name}-closure temperature"
        filepath = f"{settings.DOWNLOAD_URL}{filename}-{ap.calc.basic.random_choice(length=8)}.pdf"
        cvs = [[ap.smp.export.get_cv_from_dict(plot, **params_list) for plot in plot_data['data']]]
        filepath = ap.smp.export.export_chart_to_pdf(cvs, filename, filepath)
        export_href = '/' + filepath

        print(f"{export_href = }")
        messages.info(request, f'Success to export_chart, href: {export_href}')
        return self.JsonResponse({'status': 'success', 'href': export_href})

    def calculate_dr2(self, f, ti, ar, sar, use_ln=True, logdr2_method="plane"):
        try:
            if str(logdr2_method).lower().startswith('plane'.lower()):
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_plane(f, ti, ar=ar, sar=sar, ln=use_ln)
            elif str(logdr2_method).lower() == 'yang':
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_yang(f, ti, ar=ar, sar=sar, ln=use_ln)
            elif str(logdr2_method).lower().startswith('sphere'.lower()):
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_sphere(f, ti, ar=ar, sar=sar, ln=use_ln)
            elif str(logdr2_method).lower().startswith('Thern'.lower()):
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_thern(f, ti, ar=ar, sar=sar, ln=use_ln)
            elif str(logdr2_method).lower().startswith('cylinder'.lower()):
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_cylinder(f, ti, ar=ar, sar=sar, ln=use_ln)
            elif str(logdr2_method).lower().startswith('cube'.lower()):
                dr2, ln_dr2, wt = ap.smp.diffusion_funcs.dr2_cube(f, ti, ar=ar, sar=sar, ln=use_ln)
            else:
                raise KeyError(f"Geometric model not found: {str(logdr2_method).lower()}")
        except (Exception, BaseException) as e:
            raise ValueError

        return dr2, ln_dr2, wt

    def _calculate_tc(self, data, logdr2_method='plane', A=55, cooling_rate=10,
                      radius=100, use_ln=True, index=None, num=1):

        base = np.e if use_ln else 10
        # 读取样品信息
        [_, _, seq_value, te, ti, age, sage, ar, sar, f, dr2, ln_dr2, wt] = data
        # dr2, ln_dr2, wt = self.calculate_dr2(f, ti, ar, sar, use_ln=use_ln, logdr2_method=logdr2_method)

        @np.vectorize
        def get_da2_e_Tc(b, m):
            k1 = base ** b * ap.thermo.basic.SEC2YEAR  # k1: da2
            k2 = -10 * m * ap.thermo.basic.GAS_CONSTANT * np.log(base)  # activation energy, kJ
            try:
                # Closure temperature
                k3, _ = ap.thermo.basic.get_tc(da2=k1, sda2=0, E=k2 * 1000, sE=0, pho=0,
                                               cooling_rate=cooling_rate, A=A)
            except ValueError as e:
                # print(e.args)
                k3 = 999
            return k1, k2, k3  # da2, E, Tc

        index = np.s_[index if index is not None else list(range(len(te)))]
        each_line = [np.nan for i in range(19)]  # [b, sb, a, sa, ..., energy, se, da2, sda2, tc, stc]
        temp_err = 5
        X, Y, wtX, wtY = 10000 / np.array(te), np.array(ln_dr2), 10000 * temp_err / np.array(te) ** 2, np.array(wt)
        x, y, wtx, wty = X[index,], Y[index,], wtX[index,], wtY[index]
        Tc_list = []

        if len(x) > 0:

            # rates = []
            # for start in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            #     for cc in range(num):
            #         cooling_rate = start + cc * 10 / num
            #         if cooling_rate in rates or cooling_rate > 100:
            #             break
            #         rates.append(cooling_rate)
            rates = []

            # Arrhenius line regression
            # each_line[0:6] = ap.thermo.basic.fit(x, y, wtx, wty)  # intercept, slop, sa, sb, chi2, q
            # b (intercept), sb, a (slope), sa, mswd, dF, Di, k, r2, chi_square, p_value, avg_err_s, cov
            each_line[0:13] = ap.calc.regression.york2(x, wtx, y, wty, ri=np.zeros(len(x)))
            each_line[1] = each_line[1] * 1  # 1 sigma
            each_line[3] = each_line[3] * 1  # 1 sigma

            # monte carlo simulation with 4000 trials
            cov_matrix = np.array([[each_line[1] ** 2, each_line[12]], [each_line[12], each_line[3] ** 2]])
            mean_vector = np.array([each_line[0], each_line[2]])
            random_numbers = np.random.multivariate_normal(mean_vector, cov_matrix, 4000)
            res, cov = ap.calc.basic.monte_carlo(get_da2_e_Tc, random_numbers, confidence_level=0.95)
            da2, E, Tc = res[0:3, 0]
            # sda2, sE, sTc = np.diff(res[0:3, [1, 2]], axis=1).flatten() / 2
            sda2, sE, sTc = cov[0, 0] ** .5, cov[1, 1] ** .5, cov[2, 2] ** .5  # 95%

            each_line[13:15] = [E, sE]
            each_line[15:17] = [Tc, sTc]

            #
            # [b, sb, m, sm] = each_line[0:4]
            # # da2 = base ** b * ap.thermo.basic.SEC2YEAR  # da2
            # # sda2 = abs(base ** b * np.log(base) * ap.thermo.basic.SEC2YEAR * sb)  # sda2  1 sigma
            # da2 = base ** b
            # sda2 = abs(base ** b * np.log(base) * sb)
            # E = -10 * m * ap.thermo.basic.GAS_CONSTANT * np.log(base)  # activation energy, kJ
            # sE = abs(-10 * sm * ap.thermo.basic.GAS_CONSTANT * np.log(base))  # sE  1 sigma

            each_line[13:15] = [E, sE]
            each_line[15:17] = [da2, sda2]

            # monte carlo simulation with 4000 trials
            cov_matrix = np.array([[each_line[1] ** 2, each_line[12]], [each_line[12], each_line[3] ** 2]])
            mean_vector = np.array([each_line[0], each_line[2]])
            random_numbers = np.random.multivariate_normal(mean_vector, cov_matrix, 4000)

            for cooling_rate in rates:

                res, cov = ap.calc.basic.monte_carlo(get_da2_e_Tc, random_numbers, confidence_level=0.95)

                # da2, E, Tc = res[0:3, 0]
                # sda2, sE, sTc = 2 * cov[0, 0] ** .5, 2 * cov[1, 1] ** .5, 2 * cov[2, 2] ** .5  # 95%
                Tc = res[2, 0]
                sTc = cov[2, 2] ** .5  # 1 sigma

                each_line[17:19] = [Tc, sTc]

                Tc_list.append([cooling_rate, Tc, sTc])

        Tc_list = np.transpose(Tc_list)

        return each_line, X, Y, x, y, Tc_list

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

    def export_chart(self, request, *args, **kwargs):
        data = self.body['data']
        params = self.body['settings']
        keys = [
            "page_size", "ppi", "width", "height", "pt_width", "pt_height", "pt_left", "pt_bottom",
            "offset_top", "offset_right", "offset_bottom", "offset_left", "plot_together", "show_frame",
        ]
        params = dict(zip(keys, [int(val) if str(val).isnumeric() else val for val in params]))
        params_list = []
        print(params)
        for plot in data['data']:
            params_list.append(params.copy())
        params_list = iter(params_list)
        cvs = [[ap.smp.export.get_cv_from_dict(plot, **next(params_list)) for plot in data['data']]]

        filename = data.get('file_name', 'file_name')
        filepath = f"{settings.DOWNLOAD_URL}{filename}-{ap.calc.basic.random_choice(length=8)}.pdf"
        filepath = ap.smp.export.export_chart_to_pdf(cvs, filename, filepath, **params)
        export_href = '/' + filepath

        messages.info(request, f'Success to export_chart, href: {export_href}')
        return self.JsonResponse({'status': 'success', 'href': export_href})