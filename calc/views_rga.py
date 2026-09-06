#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2026 Yang 
# webarar - rga_views
# ==========================================
#
#
# 
"""


import csv
import json
import re
from pathlib import Path
from datetime import datetime
import base64
from django.conf import settings
from programs import http_funcs
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


# Create your views here.
gas_molar_mass = {}


class RgaView(http_funcs.ArArView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_post_method_name = []

    def get(self, request, *args, **kwargs):

        config_path = settings.SETTINGS_ROOT / 'rga.conf'
        with open(config_path, "r", encoding="utf-8") as f:
            configs = json.load(f)
        gas_molar_mass.update(configs.pop("gas_molar_mass"))

        return self.render(request, 'rga_zerotime_extrapolate.html', {
            'rga_files': get_rga_file_list(),
            'rga_files_root': str(settings.RGA_ROOT),
            'rga_configs': configs,
        })

    def rga_get_file_list(self, request, *args, **kwargs):
        return self.JsonResponse({
            'rga_files': get_rga_file_list(),
            'rga_files_root': str(settings.RGA_ROOT),
        })

    def rga_read_file(self, request, *args, **kwargs):
        relative_path = self.body.get('relative_path')
        try:
            file_path = resolve_rga_file(relative_path)
            data = open_rga_csv(file_path)
        except ValueError as error:
            return self.JsonResponse({'error': str(error)}, status=400)
        except FileNotFoundError as error:
            return self.JsonResponse({'error': str(error)}, status=404)
        except OSError as error:
            return self.JsonResponse({'error': f'Unable to read RGA file: {error}'}, status=500)

        return self.JsonResponse({
            'relative_path': file_path.relative_to(Path(settings.RGA_ROOT).resolve()).as_posix(),
            'data': data,
        })

    def rga_export_single(self, request, *args, **kwargs):
        chemicals = self.body.get('chemicals')
        parameters = self.body.get('parameters')
        sample = self.body.get('sample')

        href = settings.DOWNLOAD_ROOT / f'{sample}-fitResults.csv'
        with open(href, 'w', newline='', encoding='utf-8-sig') as file:
            export_ega_results(file, chemicals, parameters, sample)

        print(f"exported to: {href}")

        return self.FileResponse(
            open(href, 'rb'), as_attachment=True, filename=href.name,
        )

    def rga_export_multi(self, request, *args, **kwargs):
        export_files = self.body.get('files')
        if not isinstance(export_files, list) or not export_files:
            return self.JsonResponse({'error': 'At least one RGA file is required.'}, status=400)
        href = settings.DOWNLOAD_ROOT / f'fitResults.csv'
        with open(href, 'w', newline='', encoding='utf-8-sig') as file:
            export_ega_multi_results(file, export_files)

        return self.FileResponse(
            open(href, 'rb'), as_attachment=True, filename=href.name,
        )


def get_rga_file_list():
    folder = Path(settings.RGA_ROOT)
    files = []

    # A fresh local installation creates this directory from settings.py,
    # but keeping the view tolerant makes /calc/rga usable before that
    # initialization has run and in existing production installations.
    try:
        folder.mkdir(parents=True, exist_ok=True)
        entries = list(folder.rglob('*'))
    except OSError as error:
        entries = ()

    for path in entries:
        try:
            if not path.is_file():
                continue
            stat_info = path.stat()
        except OSError as error:
            continue

        mtime_ts = stat_info.st_mtime
        relative_path = path.relative_to(folder).as_posix()
        relative_parent = path.parent.relative_to(folder).as_posix()
        if relative_parent == '.':
            relative_parent = ''
        files.append({
            'filename': path.name,
            'relative_path': relative_path,
            'directory': relative_parent,
            'size': stat_info.st_size,
            'st_mtime': mtime_ts,
            'modify_time': datetime.fromtimestamp(mtime_ts).strftime('%Y-%m-%d %H:%M:%S'),
        })

    files.sort(key=lambda item: item['st_mtime'], reverse=True)
    return files


def encode_points(points, point_count):
    data = bytearray((point_count + 7) // 8)

    for point in points:
        index = point - 1
        data[index // 8] |= 1 << (index % 8)

    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def resolve_rga_file(relative_path):
    """Resolve a browser-provided RGA relative path inside ``RGA_ROOT``."""
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError('An RGA relative path is required.')

    root = Path(settings.RGA_ROOT).resolve()
    normalized = relative_path.strip().replace('\\', '/')
    candidate = (root / normalized).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise ValueError('The RGA path must stay inside the RGA data folder.') from error
    if not candidate.is_file():
        raise FileNotFoundError(f'RGA file does not exist: {relative_path}')
    return candidate


def _parse_rga_number(value):
    """Convert an RGA CSV value to a JSON-safe number when possible."""
    text = str(value or '').strip().replace(',', '')
    if not text:
        return None
    try:
        number = float(text)
    except (TypeError, ValueError):
        return text
    return int(number) if number.is_integer() else number


def open_rga_csv(file_path):
    """Parse the metadata and scan table from an SRS RGASoft CSV export."""
    rows = []
    last_error = None
    for encoding in ('utf-8-sig', 'utf-8', 'cp1252'):
        try:
            with open(file_path, 'r', encoding=encoding, newline='') as source:
                rows = list(csv.reader(source))
            break
        except UnicodeDecodeError as error:
            last_error = error
    else:
        raise ValueError(f'Unable to decode RGA file: {last_error}')

    parameters = {}
    sensitivity_by_name = {}
    scan_header_index = None
    scan_header = None
    for index, row in enumerate(rows):
        cells = [str(cell).strip() for cell in row]
        if not cells:
            continue
        key = cells[0]
        if key.lower().startswith('scan#') and len(cells) > 1:
            scan_header_index = index
            scan_header = cells
            break
        if key.lower() == 'chemical name':
            for chemical_row in rows[index + 1:]:
                name = str(chemical_row[0]).strip() if chemical_row else ''
                if not name:
                    continue
                if name.lower().startswith('scan#'):
                    break
                sensitivity = _parse_rga_number(chemical_row[1] if len(chemical_row) > 1 else '')
                sensitivity_by_name[name] = sensitivity
            continue
        if len(cells) > 1 and key:
            parameters[key] = _parse_rga_number(cells[1])

    if scan_header_index is None or scan_header is None:
        raise ValueError('No scan table was found in the RGA file.')

    chemical_names = []
    for header in scan_header[2:]:
        name = header.strip()
        if not name:
            continue
        name = re.sub(r'\s*\([^)]*\)\s*$', '', name).strip()
        chemical_names.append(name)

    values = [[] for _ in chemical_names]
    times = []
    for row in rows[scan_header_index + 1:]:
        cells = [str(cell).strip() for cell in row]
        if len(cells) < 2 or not cells[0] or not cells[1]:
            continue
        if not re.match(r'^[-+]?\d+(?:\.\d+)?$', cells[0]):
            continue
        times.append(_parse_rga_number(cells[1]))
        for chemical_index in range(len(chemical_names)):
            value = cells[chemical_index + 2] if chemical_index + 2 < len(cells) else ''
            values[chemical_index].append(_parse_rga_number(value))

    chemicals = []
    for name, chemical_values in zip(chemical_names, values):
        chemicals.append({
            'name': name,
            'values': chemical_values,
            'sensitivity_factor': sensitivity_by_name.get(name, 1),
            'mass': gas_molar_mass.get(name.lower(), 1),
            'selected_points': encode_points([i for i in range(1, len(chemical_values)+1)], len(chemical_values)),
            'point_selection_encoding': 'bitset-base64url-v1'
        })

    return {
        'sample': Path(file_path).stem,
        'parameters': parameters,
        'time': times,
        'chemicals': chemicals,
    }


def export_ega_results(file, gas_data, parameters, sample_name):
    param_names = [
        'Start Mass', 'Stop Mass', 'Scan Rate', 'Detector', 'CEM Gain',
        'Filament Current', 'Partial Pressure Sensitivity Factor',
        'Ion Energy', 'Focus Voltage',
    ]
    # CSV 表头
    headers = [
        'Chemical', 'Fit Method', 'Mass', 'Sensitivity Factor',
        'Selected Points', 'ZeroTime Value', 'Normalized Value',
        'Fitting Coefficients', 'Status',
    ]

    # 处理每一行数据
    rows = []
    total_value = ''
    normalized_total_value = ''
    for item in gas_data:
        # 基础字段
        row = {
            'Chemical': item['name'],
            'Fit Method': item['method'] if item['selected'] else 'None',
            'Mass': item['mass'],
            'Sensitivity Factor': item['sensitivityFactor'],
            'Selected Points': ';'.join(map(str, item['selectedPoints'])),
            'ZeroTime Value': '',
            'Normalized Value': '',
            'Fitting Coefficients': '',
            'Status': item.get('status', '')
        }

        # 处理嵌套的拟合结果
        fit_res = item.get('fitResult')
        if isinstance(fit_res, dict):
            row['ZeroTime Value'] = fit_res.get('zeroTime', '')
            params = fit_res.get('parameters', {})
            row['Fitting Coefficients'] = str(params)

        rows.append(row)

    # 这里是对原rows字典的引用，会同步修改
    selected_rows = [
        (item, row)
        for item, row in zip(gas_data, rows)
        if item.get('selected', False)
    ]

    selected_values = [
        _finite_decimal(row['ZeroTime Value'])
        for _, row in selected_rows
    ]

    can_normalize = (
        bool(selected_rows)
        and all(value is not None for value in selected_values)
    )

    if can_normalize:
        total_value = sum(selected_values, Decimal('0'))

        if total_value != 0:
            for (_, row), value in zip(selected_rows, selected_values):
                row['Normalized Value'] = (
                    value / total_value * Decimal('100')
                )

        normalized_total_value = 100

    writer = csv.writer(file)

    writer.writerow(['Sample', sample_name])
    writer.writerow(['RGA ID', parameters['RGA ID']])

    for param_name in param_names:
        writer.writerow([param_name, parameters[param_name.lower().replace(' ', '_')]])

    writer.writerow([])

    writer.writerow(headers)

    writer.writerows([
        [row[column] for column in headers]
        for row in rows
    ])

    writer.writerow(['', '', '', '', '', total_value, normalized_total_value, '', ''])


def export_ega_multi_results(file, multi_files):
    param_names = [
        'Start Mass', 'Stop Mass', 'Scan Rate', 'Detector', 'CEM Gain',
        'Filament Current', 'Partial Pressure Sensitivity Factor',
        'Ion Energy', 'Focus Voltage',
    ]

    chemical_names = []
    seen_names = set()

    for source_file in multi_files:
        for chemical in source_file.get('data', {}).get('chemicals', []):
            name = str(chemical.get('name') or '').strip()
            if name and name not in seen_names:
                seen_names.add(name)
                chemical_names.append(name)

    headers = [
        'File', 'Sample', 'RGA ID', *param_names, '',
        'Chemicals', *chemical_names, 'Total', '',
        'Normalized', *chemical_names, 'Total',
    ]
    records = [headers]

    for entry in multi_files:
        data = entry.get('data', {})
        parameters = data.get('parameters') or {}
        chemicals = {
            chemical.get('name'): chemical
            for chemical in data.get('chemicals') or []
            if chemical.get('name')
        }

        parameter_values = []
        for param_name in param_names:
            key = param_name.lower().replace(' ', '_')
            parameter_values.append(parameters.get(key, parameters.get(param_name, '')))

        chemical_values = []
        for chemical_name in chemical_names:
            chemical = chemicals.get(chemical_name, {})
            fit_result = chemical.get('fitResult')
            if not isinstance(fit_result, dict):
                fit_result = chemical.get('fit_result')
            value = fit_result.get('zeroTime', fit_result.get('zero_time', '')) \
                if isinstance(fit_result, dict) else ''
            chemical_values.append(value)

        decimal_values = [_finite_decimal(value) for value in chemical_values]
        total = ''
        normalized_values = [''] * len(chemical_names)
        normalized_total = ''
        if chemical_values and all(value is not None for value in decimal_values):
            decimal_total = sum(decimal_values, Decimal('0'))
            total = decimal_total
            if decimal_total != 0:
                quantum = Decimal('0.000001')
                normalized_values = [
                    (value / decimal_total * Decimal('100')).quantize(
                        quantum,
                        rounding=ROUND_HALF_UP,
                    )
                    for value in decimal_values
                ]
                rounding_difference = Decimal('100.000000') - sum(
                    normalized_values,
                    Decimal('0'),
                )
                normalized_values[-1] += rounding_difference
                normalized_total = 100

        records.append([
            entry.get('relative_path', ''),
            data.get('sample', ''),
            parameters.get('RGA ID', parameters.get('rga_id', '')),
            *parameter_values,
            '',
            'Zero-time Value',
            *[
                _format_decimal(value) if value != '' else ''
                for value in chemical_values
            ],
            _format_decimal(total),
            '',
            'Normalized Value',
            *[
                _format_decimal(value) if value != '' else ''
                for value in normalized_values
            ],
            normalized_total,
        ])

    writer = csv.writer(file)
    writer.writerows(zip(*records))


def _finite_decimal(value):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return number if number.is_finite() else None


def _format_decimal(value, places=6):
    number = _finite_decimal(value)
    if number is None:
        return ''
    quantum = Decimal(1).scaleb(-places)
    return format(number.quantize(quantum, rounding=ROUND_HALF_UP), 'f')
