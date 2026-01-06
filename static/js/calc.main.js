const FILLED_POINTS_COLOR = '#337ab7';
const rich_format = {
    sub: {verticalAlign: "bottom",fontSize: 10, fontFamily: 'Microsoft Sans Serif', fontWeight: 'bold'},
    sup: {verticalAlign: "top", fontSize: 10, fontFamily: 'Microsoft Sans Serif', fontWeight: 'bold'},
};
// Basic functions
function myParse(myString) {
    // Note that \\" to keep an escape character before double quote characters
    if ( ! (typeof myString === 'string' || myString instanceof String)) {return myString}
    myString = myString.replace(/\bNaN\b/g, '"*isNaN*"')
                       .replace(/-\bInfinity\b/g, '"*isNegativeInfinity*"')
                       .replace(/\bInfinity\b/g, '"*isInfinity*"');
    return JSON.parse(myString, function (key, value) {
        if (value === "*isNaN*") {
            return NaN;
        }
        if (value === "*isInfinity*") {
            return Infinity;
        }
        if (value === "*isNegativeInfinity*") {
            return -Infinity;
        }
        return value;
    });
}
function closePopupMessage(confirmation=true) {
    let popupContainer = document.getElementById('popupContainer');
    let popupMessage = document.getElementById('popupMessage');
    let popupTitle = document.getElementById('popupTitle');
    let continueButton = document.getElementById('popupContinueButton');
    let cancelButton = document.getElementById('popupCancelButton');
    popupContainer.style.display = 'none';
    popupTitle.textContent = "";
    popupMessage.textContent = "";
    continueButton.style.display = 'none';
    cancelButton.style.display = 'none';
    return confirmation;
}
function showPopupMessage(title, message, show_button=true, show_cancel=false, time=undefined) {
    // 获取所需元素
    let popupContainer = document.getElementById('popupContainer');
    let popupTitle = document.getElementById('popupTitle');
    let popupMessage = document.getElementById('popupMessage');
    let continueButton = document.getElementById('popupContinueButton');
    let cancelButton = document.getElementById('popupCancelButton');

    // 显示弹窗
    popupTitle.textContent = title;
    popupMessage.innerHTML = message;
    popupContainer.style.display = 'block';
    if (show_button) {
        popupContainer.onclick = () => false;
        continueButton.style.display = 'inline-block';
        if (show_cancel) {
            cancelButton.style.display = 'inline-block';
        }
        continueButton.focus();
    } else {
        if (time === undefined) {
            time = 1500;
            popupContainer.onclick = () => {closePopupMessage(false)};
        } else {
            popupContainer.onclick = () => false;
        }
        delay(time)
            .then((result) => {
                console.log(result); // 输出异步操作的结果
                closePopupMessage(true);
            })
            .catch((error) => {
                console.error('Error:', error); // 输出错误信息
                closePopupMessage(false);
            });
    }

    return new Promise(function(resolve, reject) {
        $(continueButton).off('click').on('click', function() {
            closePopupMessage(true);
            resolve(true);
        })
        $(cancelButton).off('click').on('click', function() {
            closePopupMessage(false);
            resolve(false);
        })
    });

}
function showErrorMessage(XMLHttpRequest, textStatus, errorThrown) {
    let text = `Status: ${textStatus}<br>Message: ${XMLHttpRequest.responseJSON?.msg}`;
    showPopupMessage("Error", text, true);
}
const stringToBoolean = (stringValue) => {
    if (typeof stringValue === "boolean") {
        return stringValue;
    }
    switch(stringValue?.toLowerCase().trim()){
        case "true":
        case "1":
          return true;
        default:
          return false;
    }
}
const delay = ms => new Promise((resolve, reject) => {
    setTimeout((ms) => {
        // 模拟异步操作成功的情况，返回结果
        resolve(`Waited for some seconds.`);
    }, ms); // 延迟2秒执行
});
function countOccurrences(str, target) {
    const regex = new RegExp(target, 'g');
    const matches = str.match(regex);
    return matches ? matches.length : 0;
}
// extrapolate-functions
function addNametoBlankList(name) {
    let li = document.createElement('li');
    li.className = "list-group-item";
    li.innerText = name;
    li.onclick = function () {
        let input = $("#inputBlankSequences");
        let addName = (item) => {input.val(input.val() + item + ';')};
        let removeName = (item) => {input.val(input.val().replace(item + ';', ''))};
        input.val().includes(name)?removeName(name):addName(name);
    }
    document.getElementById('listGroupBlankName').appendChild(li);
    let btn_show = document.createElement('button');
    btn_show.type = 'button';
    btn_show.className = "list-group-item";
    btn_show.innerText = "...";
    btn_show.onclick = function (event){
        $('#modal-blank-info-title').text(name);
        let tableContents = getBlankInfo(name);
        $('#experiment-time').text(tableContents[0].time);
        $('#table-blank-info').bootstrapTable('load', tableContents);
        $('#modal-blank-info').modal('show');
    };
    document.getElementById('listGroupBlankBtn').appendChild(btn_show);
}
function addNewBlankButtonClicked() {
    let newBlankName = $('#outputBlankSequences').val();
    $('#outputBlankSequences').val('');
    $('#inputBlankSequences').val('');
    let newNameList = newBlankName.split(';');
    let existing_blank_names = myRawData.sequence.filter((seq, index) => seq.is_blank).map(
        (seq, index) => seq.name)
    let not_blanks = [];
    for (let i = 0; i < newNameList.length; i++) {
        let name = newNameList[i];
        let new_sequence = newSequencesList.filter((v, _i) => v.name === name)[0]
        if (!new_sequence.is_blank) {
            not_blanks.push(`${name}`);
            continue;
        }
        if (existing_blank_names.includes(name)) {
            showPopupMessage("Information",`Blank with name ${name} exists.`, true);
            continue;
        }
        addNametoBlankList(name);
        let option = document.createElement("option");
        option.value = name;
        option.innerText = name;
        myRawData.sequence.push(...newSequencesList.filter((v, _i) => v.name === name));
    }
    if (not_blanks.length > 0) {
        showPopupMessage("Information", `The following sequences are not blanks:\n`+not_blanks.join(','), true);
    }
    $('#table-sequences').bootstrapTable('destroy');
    initialTable(myRawData.sequence.filter((v, i) => v.is_blank).map((v, i) => v.name));
    updateSequenceTable();
    // Note that estimated blank sequence will be ignored for automatically sorting
    corrBlankMethodChanged(myRawData.sequence.filter((seq, index) => seq.is_blank && !seq.is_estimated));
}
function rawFilesChanged() {
    const formDom = document.getElementById("rawFileForm");
    const fileInput = formDom.querySelector('input[type="file"]');
    const fileCount = fileInput.files.length;
    const maxNumberFiles = 100;
    let table = $('#raw_file_list');
    if (fileCount === 0) {return}
    if (fileCount > maxNumberFiles) {
        showPopupMessage("Error", `The number of files (${fileCount}) exceeded MAX NUMBER (${maxNumberFiles})`, true);
        return
    }
    let formData = new FormData(formDom);
    $.ajax({
        url: url_raw_files_changed,
        type: 'POST',
        data: formData,
        async : true,
        processData : false,
        contentType : false,
        mimeType: "multipart/form-data",
        success: function(res){
            $('#file-input-1').val('');
            let files = JSON.parse(res).files;
            let data = table.bootstrapTable('getData');

            $.each(files, function (index, file) {
                let filter_options = `${file.filter_list.map((item, _) => {
                    if (item.toUpperCase().includes(file.filter.toUpperCase())) { return "<option selected>" + item + "</option>" }
                    return "<option>" + item + "</option>"
                }).join("")}`;
                table.bootstrapTable('insertRow', {index: data.length + index,
                    row: {
                        'file_name': file.name,
                        'file_path': file.path,
                        'filter': `<select class="input-sm input-filter-selection" style="width: 200px" onchange="change_input_filter(this)">${filter_options}</select>`,
                        'operation': '<button type="button" class="btn btn-danger" onclick="removeRawFile(id)" ' +
                            'id="btn-raw-file-' + data.length +'">Remove</button>',
                    }
                });
                document.getElementById('input-filter-title-selection').innerHTML = filter_options;
            })
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    })
}
function showFilesToDelete() {
    let table = $('#uploaded_file_list');
    $.ajax({
        url: url_get_files_to_delete,
        type: 'POST',
        async : true,
        contentType:'application/json',
        success: function(res){
            let files = res.files;
            table.bootstrapTable('removeAll');
            $.each(files, function (index, file) {
                table.bootstrapTable('insertRow', {index: index,
                    row: {
                        'number': index + 1,
                        'file_path': file.path,
                        'file_name': file.name,
                        'insert_time': file.time,
                        'operation': '<button type="button" class="btn btn-danger" onclick="deleteUploadedFilesOnTable(id)" ' +
                            'id="btn-raw-file-' + index +'">Delete</button>',
                    }
                });
            })
            table.bootstrapTable('refresh');
        }
    })
}
function deleteUploadedFilesOnTable(row_index) {
    let table = $('#uploaded_file_list');
    let data = table.bootstrapTable('getData');
    const rowIndexes = Array.isArray(row_index) ? row_index : (typeof row_index === 'string' && row_index.trim() !== '')
            ? [Number(row_index.slice(13))] : [];
    const paths = [];
    rowIndexes.forEach(index => {
        const targetRow = data.find(row => row.number === index + 1);
        if (targetRow) { paths.push(targetRow.file_path || ''); }
    });
    $.ajax({
        url: url_delete_selected_files,
        type: 'POST',
        data: JSON.stringify({
            'indexes': rowIndexes,
            'paths': paths,
        }),
        contentType:'application/json',
        success: function(res){
            $.each(rowIndexes, function (index, each) {
                table.bootstrapTable('updateRow', {index: each,
                    row: {
                        'operation': '<button type="button" class="btn btn-grey">Deleted</button>',
                    }
                })
            });
            showPopupMessage('Information', res.message, true);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    })
}
function deleteSelectedFiles() {
    let table = $('#uploaded_file_list');
    let data = table.bootstrapTable('getData');
    let rowIndexes = [];
    data.forEach(row => {
        // indexes based on 0
        if (row['checked']) { rowIndexes.push(Number(row['number']) - 1) }
    });
    deleteUploadedFilesOnTable(rowIndexes);
}
function deleteAllFiles() {
    let table = $('#uploaded_file_list');
    let rowCount = table.bootstrapTable('getOptions').totalRows;
    let rowIndexes = Array.from({ length: rowCount }, (_, index) => index);
    deleteUploadedFilesOnTable(rowIndexes);
}
function change_input_filter(row, index) {
    // This function is used to keep selected options when rows inserted or removed
    if (!index) { index = row.selectedIndex }
    let table = $('#raw_file_list');
    let current_data = table.bootstrapTable('getData');
    let tr = row.parentElement.parentElement;
    let row_index = tr.getAttribute("data-index");
    let opts = row.options;
    for (let i=0;i<opts.length;i++){
        $(opts[i]).attr("selected", index === i);
    }
    current_data[row_index].filter = row.outerHTML;
    table.bootstrapTable('updateRow', {index: row_index,
        row: current_data
    })
}
function change_filter_at_title() {
    let val = document.getElementById('input-filter-title-selection').value;
    const table_data = $('#raw_file_list').bootstrapTable('getData');
    $.each(document.getElementsByClassName('input-filter-selection'), function (index, each) {
        if (table_data[index]['checked']) {
            each.value = val;
        }
    });
    updateRawFileTable()
}
function updateRawFileTable() {
    let filters = [];
    // console.log($('#raw_file_list').bootstrapTable('getData'));
    // console.log($('#raw_file_list').bootstrapTable('getData')[0].checked);
    $('.input-filter-selection').each((index, ele) => {
        filters[index] = ele.options[ele.selectedIndex]?.innerText;
    });
    $('#raw-file-table-input').val(JSON.stringify({
        'files': $('#raw_file_list').bootstrapTable('getData').map((item, index) => {
            return {
                'file_name': item['file_name'], 'file_path': item['file_path'],
                'filter': filters[index], 'checked': item['checked']
            }
        })
    }))
}
function removeRawFile(unique_id) {
    let table = $('#raw_file_list');
    let data = table.bootstrapTable('getData');
    data.splice(Number(unique_id.slice(13)), 1);
    for (let i=Number(unique_id.slice(13));i<data.length;i++) {
        data[i].operation = '<button type="button" class="btn btn-danger" onclick="removeRawFile(id)" ' +
            'id="btn-raw-file-' + i +'">Remove</button>'
    }
    table.bootstrapTable('load', data);
    $('#raw-file-table-input').val(JSON.stringify({'files': table.bootstrapTable('getData')}))
}
function getEmptyBlank() {
    $.ajax({
        url: url_raw_empty_blank,
        type: 'POST',
        data: JSON.stringify({
            'new_blank_name': document.getElementById('outputBlankSequences').value,
            'cache_key': myRawCacheKey,
        }),
        contentType:'application/json',
        dataType: 'text',
        success: function(res){
            res = myParse(res);
            let new_sequence = res.new_sequence;
            $('#outputBlankSequences').val(new_sequence.name);
            newSequencesList.push(new_sequence);
        }
    })
}
function importBlank() {
    if ($('#file-input-import-blank').val() === '') {return}
    $('#file-input-cache-key').val(myRawCacheKey);
    let formData = new FormData(document.getElementById("form-import-blank-file"));
    $.ajax({
        url: url_raw_import_blank_file,
        type: 'POST',
        data: formData,
        processData : false,
        contentType : false,
        // contentType: 'application/json',
        mimeType: "multipart/form-data",
        dataType: "text",
        success: function(res){
            $('#file-input-import-blank').val('');
            res = myParse(res);
            let new_sequences = res.sequences;
            newSequencesList.push(...new_sequences);
            $('#outputBlankSequences').val(new_sequences.map((v, i) => v.name).join(';'));
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
        //     function (res) {
        //     showPopupMessage("Information", myParse(res.responseText).error);
        // }
    })
}
function export_sequence() {
    let modal = $('#modal-export-sequence');
    let modal_body = $('#modal-export-sequence-body');
    if (!modal.is(':visible')) {
        btnExtrapolateSelectAll.text("Select All");
        modal_body.empty();
        $.each(myRawData.sequence.filter((item, index) => !item.is_estimated), (index, sequence) => {
            let div = document.createElement('div');
            let checkbox = document.createElement('input');
            let label = document.createElement('label');
            checkbox.type = "checkbox";
            checkbox.id = sequence.name;
            checkbox.style.marginLeft = "0px";
            checkbox.className = "checkbox-extrapolate-export-sequence";
            div.className = "checkbox-inline checkbox";
            div.style.width = "250px";
            div.style.margin = "0 0 0 0";

            label.htmlFor = sequence.name;
            label.appendChild(document.createTextNode(sequence.name));

            div.append(checkbox);
            div.append(label);
            modal_body.append(div);
        })
        modal.modal('show');
    } else {
        let selected = $('.checkbox-extrapolate-export-sequence').map((index, item) => item.checked).get();
        if (selected.filter((item, index) => item).length === 0) {
            return
        }
        $.ajax({
            url: url_raw_export_sequence,
            type: 'POST',
            data: JSON.stringify({
                'selected': selected,
                'is_blank': selected.map((item, index) => myRawData.sequence[index].is_blank),
                'fitting_method': selected.map((item, index) => myRawData.sequence[index].fitting_method),
                'cache_key': myRawCacheKey}),
            processData : false,
            contentType : false,
            mimeType: "multipart/form-data",
            success: function(res){
                res = myParse(res);
                document.getElementById("export_sequence_link").href = res.href;
                document.getElementById("export_sequence_link").click();
            }
        })
        document.getElementById("export_sequence_link").href = '';
        modal.modal('hide');
    }
}
function check_regression() {
    // let selectedSequences = $('#table-sequences').bootstrapTable('getSelections');
    // selectedSequences.map((each, index) => {
    //     each['blank'] = $('#blank-sele'+each.id).find("option:selected").text();
    // })
    $.ajax({
        url: url_raw_check_regression,
        type: 'POST',
        data: JSON.stringify({
            'cache_key': myRawCacheKey,
        }),
        contentType:'application/json',
        success: function(res){
            let btns = document.getElementsByName('sequenceBtn');
            for (let i of res.failed){
                btns[i-1].className = 'btn btn-warning btn-no-outline';
            }
            showPopupMessage("Information", res.msg, true);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    })
}

function getExportedData(table){
    let settings = (ele) => ele.options[ele.selectedIndex].innerText;
    return table.bootstrapTable('getData').map((item, index) => {
        return {
            'checked': item['checked'],
            'file_name': item['file_name'],
            'file_path': item['file_path'],
            'diagram': settings($('.input-filter-selection-diagram')[index]),
            'setting': settings($('.input-filter-selection-setting')[index]),
            'position': settings($('.input-filter-selection-position')[index]),
        }
    })
}
// export to pdf
function filesToExportChanged() {
    let table = $('#export_arr_file_list');
    let data = getExportedData(table);
    if ($('#files_to_export').val() === '') {return}
    let formData = new FormData(document.getElementById("editExportForm"));
    $.ajax({
        url: url_multi_files,
        type: 'POST',
        data: formData,
        async : true,
        processData : false,
        contentType : false,
        mimeType: "multipart/form-data",
        success: function(res){
            $('#files_to_export').val('');
            let files = JSON.parse(res).files;
            let diagram = 'Age Spectra';
            let setting = 'spectra';
            let data_length = data.length;
            $.each(files, function (index, file) {
                table.bootstrapTable('insertRow', {index: data.length + index,
                    row: {
                        'file_name': file.name,
                        'file_path': file.path,
                        'diagram': `<select class="input-sm input-filter-selection-diagram" style="width: 100px">${diagram_list.map((item, _) => {
                            if (item.toUpperCase() === diagram.toUpperCase()) {
                                return "<option selected>" + item + "</option>"
                            }
                            return "<option>" + item + "</option>"
                        }).join("")}$</select>`,
                        'setting': `<select class="input-sm input-filter-selection-setting" style="width: 100px">${setting_list.map((item, _) => {
                            if (item.toUpperCase() === setting.toUpperCase()) {
                                return "<option selected>" + item + "</option>"
                            }
                            return "<option>" + item + "</option>"
                        }).join("")}$</select>`,
                        'position': `<select class="input-sm input-filter-selection-position" style="width: 50px">${position_list.map((item, _) => {
                            if (item.toUpperCase() === (data_length + index + 1).toString().toUpperCase()) {
                                return "<option selected>" + item + "</option>"
                            }
                            return "<option>" + item + "</option>"
                        }).join("")}$</select>`,
                    }
                })
            })
            $.each(data, function(index, row) {
                table.bootstrapTable(row.checked ? 'check' : 'uncheck', index);
                $('.input-filter-selection-diagram').eq(index).val(row.diagram);
                $('.input-filter-selection-setting').eq(index).val(row.setting);
                $('.input-filter-selection-position').eq(index).val(row.position);
            })
        }
    })
}
function createSmChart(container, option) {
    let chart = echarts.init(container, null, {renderer: 'svg'});
    chart.setOption(getExtrapolateDefaultOption());
    chart.setOption(option);
    chart.setOption({
        title: {left: '5%', top:'5%', textStyle: {fontSize: 12, fontWeight: 'normal'}}, legend: {show: false},
    })
    return chart
}
function showDatabase(ele, callback=null) {
    //
}
function showParamProject(ele, param_type, isProRadio=true, callback=null) {
    if (ele && !param_type) {
        if (ele.id.toString().includes('irra')) {
            param_type = "irra";
        } else if (ele.id.toString().includes('calc')) {
            param_type = "calc";
        } else if (ele.id.toString().includes('smp')) {
            param_type = "smp";
        } else if (ele.id.toString().includes('inputFilter')) {
            param_type = "input-filter";
        } else if (ele.id.toString().includes('thermo')) {
            param_type = "thermo";
        }  else if (ele.id.toString().includes('export')) {
            param_type = "export-pdf";
        } else { return }
    }
    if (!$(`#${param_type}ParamsRadio1`).is(':checked') && isProRadio) { return }
    if (!$(`#${param_type}ParamsRadio2`).is(':checked') && !isProRadio) { return }
    let name = ele.value? ele.value : ele;
    $.ajax({
        url: url_change_param_objects,
        type: 'POST',
        data: JSON.stringify({
            'name': name,
            'type': param_type,
            'cache_key': typeof cache_key !== 'undefined'? cache_key: undefined,
        }),
        async: true,
        contentType:'application/json',
        success: function(res){
            if (param_type === "irra") {
                let irraInput = document.getElementsByClassName(`${ param_type }-params`);
                irradiationCyclesChanged(Number(res.param[28]));
                $.each(irraInput, function (index, each) {
                    each.value=res.param[index];
                });
            }
            if (param_type === "input-filter" || param_type === "calc" || param_type === "smp" || param_type === "thermo" || param_type === "export-pdf") {
                let input_box = document.getElementsByClassName(`${ param_type }-params`);
                let check_Box = document.getElementsByClassName(`${ param_type }-check-box`);
                $.each(input_box, function (index, each) {
                    each.value=res.param[index];
                });
                $.each(check_Box, function (index, each) {
                    each.checked=stringToBoolean(res.param[index+input_box.length]);
                });
                initialRatioSelectChanged();
            }
            if (callback) {callback()}
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    })
}
function showOnlyMyUploads(ele, param_type) {
    if (ele && !param_type) {
        if (ele.id.toString().includes('irra')) {
            param_type = "irra";
        } else if (ele.id.toString().includes('calc')) {
            param_type = "calc";
        } else if (ele.id.toString().includes('smp')) {
            param_type = "smp";
        } else if (ele.id.toString().includes('inputFilter')) {
            param_type = "input-filter";
        } else if (ele.id.toString().includes('thermo')) {
            param_type = "thermo";
        }  else if (ele.id.toString().includes('export')) {
            param_type = "export-pdf";
        } else { return }
    }
    if ($(`#${param_type}ParamsRadio2`).is(':checked')) { return }
    $.ajax({
        url: url_get_param_names,
        type: 'POST',
        data: JSON.stringify({
            'checked': ele.checked,
            'type': param_type,
        }),
        async: true,
        contentType:'application/json',
        success: function(res){
            const select = document.querySelector('select[name="projectName"]');
            if (select) {
                select.innerHTML = '';
                res.names.forEach(name => {
                    const option = document.createElement('option');
                    option.value = name;
                    option.textContent = name;
                    select.appendChild(option);
                });
            }
            if (res.names.length > 0) {
                showParamProject(select);
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    })
}
function changeSubmitType() {
    if ($('input[name="paramsRadio"][value="option2"]').is(':checked')) {
        $('#submitBtn').text('Submit');
        $('#deleteBtn').hide();
        $('select[name="projectName"]').attr('disabled', true);
    } else {
        $('#submitBtn').text('Save');
        $('#deleteBtn').show();
        $('select[name="projectName"]').attr('disabled', false);
    }
}
function chartScatterClicked(data_indexes) {
    $.ajax({
        url: url_raw_data_points_click,
        type: 'POST',
        data: JSON.stringify({
            'selectionForAll': document.getElementById("applySelectionToAll").checked,
            'sequence_index': current_page-1,
            'data_index': data_indexes,
            'isotopic_index': getCurrentIsotope(),
            'cache_key': myRawCacheKey,
        }),
        contentType:'application/json',
        dataType : 'text',
        success: function(res){
            res = myParse(res);
            myRawData.sequence[current_page - 1] = res.sequence;
            updateCharts(smCharts, chartBig, current_page-1, false,
                myRawData.sequence[current_page - 1].fitting_method);
        },
    })
}
function corrBlankMethodChanged(blank_sequences=[]) {
    blank_sequences = blank_sequences.length === 0?myRawData.sequence.filter(
        (seq, index) => seq.is_blank && (!seq.is_estimated)):blank_sequences;
    let unknown_sequences = myRawData.sequence.filter((seq, index) => !seq.is_blank);
    if (blank_sequences.length === 0 || unknown_sequences.length === 0) {return}
    for (let i=0;i<blank_sequences.length;i++){
        blank_sequences[i].index = new Date(blank_sequences[i].datetime).getTime();
    }
    for (let i=0;i<unknown_sequences.length;i++){
        unknown_sequences[i].index = new Date(unknown_sequences[i].datetime).getTime();
    }
    let matched_blank_name = [];
    switch ($('#corrBlankMethod').val()) {
        case "0":
            matched_blank_name = unknown_sequences.map(function (v, i) {
                for (let _i = blank_sequences.length - 1; _i >= 0; _i --) {
                    if (blank_sequences[_i].index < v.index) {
                        return blank_sequences[_i].name
                    }
                }
                return blank_sequences[0].name
            })
            break
        case "1":
            matched_blank_name = unknown_sequences.map(function (v, i) {
                for (let _i = 0; _i < blank_sequences.length; _i ++) {
                    if (blank_sequences[_i].index > v.index) {
                        return blank_sequences[_i].name
                    }
                }
                return blank_sequences[blank_sequences.length - 1].name
            })
            break
        case "2":
            matched_blank_name = unknown_sequences.map(function (v, i) {
                if (blank_sequences[0].index > v.index) {
                    return blank_sequences[0].name
                }
                if (blank_sequences[blank_sequences.length - 1].index < v.index) {
                    return blank_sequences[blank_sequences.length - 1].name
                }
                let a = blank_sequences.filter(function (_v, _i) {
                    return v.index > _v.index && v.index < blank_sequences[_i + 1].index
                })[0]
                let b = blank_sequences[blank_sequences.indexOf(a) + 1]
                if (Math.abs(a.index - v.index) <= Math.abs(b.index - v.index)) {
                    return a.name
                } else {
                    return b.name
                }
            })
            break
        case "3":
            matched_blank_name = unknown_sequences.map(function (v, i) {
                return "Interpolated Blank"  // -1 for interpolated blank
            })
            break
        default:
            break
    }
    $.each(matched_blank_name, function (index, item) {
        // If some of selected blank sequences don't exist, the selected option will be null
        $('#blank-sele'+Number(index+1)).val(item);
    })
}
function deleteParamObject(type) {
    editParams({
        url: url_edit_param_object,
        name: $('#name3').val(),
        pin: $('#pin3').val(),
        email: '',
        params: getParamsByObjectName(type),
        type: type,
        flag: 'delete'});

}
function saveParamObject(type) {
    editParams({
        url: url_edit_param_object,
        name: $('#name2').val(),
        pin: $('#pin2').val(),
        email: '',
        params: getParamsByObjectName(type),
        type: type,
        flag: 'update'});

}
function submitParamObject(type) {
    editParams({
        url: url_edit_param_object,
        name: $('#name1').val(),
        pin: $('#pin1').val(),
        email: $('#email1').val(),
        params: getParamsByObjectName(type),
        type: type,
        flag: 'create'});

}
function editParams(flag) {
    $.ajax({
        url: flag.url,
        type: 'POST',
        data: JSON.stringify({
            'name': flag.name,
            'pin': flag.pin,
            'email': flag.email,
            'params': flag.params,
            'type': flag.type,
            'flag': flag.flag,
        }),
        contentType:'application/json',
        success: function(res){
            $('#modal-submit').modal('hide');
            $('#modal-delete').modal('hide');
            $('#modal-save').modal('hide');
            // initialize input
            $('#modal-submit').find($('input:not(:empty)')).val('');
            $('#modal-save').find($('input:not(:empty)')).val('');
            if (flag.flag === 'create') {
                showPopupMessage('Information', 'Params set created!', false);
            }
            if (flag.flag === 'delete') {
                showPopupMessage('Information', 'Params set deleted!', false);
            }
            if (flag.flag === 'update') {
                showPopupMessage('Information', 'Params set updated!', false);
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    })
}
function fitMethodChanged() {
    let sel = $('#fitMethod');
    // if (document.getElementById("applyFitMethodToAll").checked) {
    //     for (let i in [0, 1, 2, 3, 4]) {
    //         for (let j=0; j<myRawData.sequence_num; j++) {
    //             myRawData.sequence[j].fitting_method[i] = fit_idx;
    //         }
    //     }
    // }
    sel.blur();  // This is to let select element ignore key operations after changes
                 // otherwise left/right arrow key will change page and also change fitting method.
    $.ajax({
        url: url_raw_change_fitting_method,
        type: 'POST',
        data: JSON.stringify({
            'sequence_index': current_page - 1,
            'isotope_index':getCurrentIsotope(),
            'fitting_index': Number(sel.val()),
            'cache_key': myRawCacheKey}),
        processData : false,
        contentType : false,
        mimeType: "multipart/form-data",
        success: function(res){
            myRawData.sequence[current_page-1].fitting_method[getCurrentIsotope()] = Number(sel.val());
            showSequence(current_page);
        }
    })
}
function getAverageofBlanks() {
    let names = document.getElementById('inputBlankSequences').value;
    let separator = names.includes(';') ? ';' : ' ';
    let nameList = names.split(separator);
    if (nameList.indexOf('') !== -1) {nameList.splice(nameList.indexOf(''), 1)}
    let blanksInfos;
    try {
        blanksInfos = nameList.map(function (name, index) {
            if (name !== '') {return getBlankInfo(name);}
        });
    } catch (e) {
        let text = "The blank sequences don\\'t exist. Please check if a whitespace may be in the names and use a semicolon as a delimiter.";
        showPopupMessage('Information', text, false);
        return
    }
    $.ajax({
        url: url_raw_average_blanks,
        type: 'POST',
        data: JSON.stringify({
            'blanks': blanksInfos,
            'new_blank_name': document.getElementById('outputBlankSequences').value,
            'cache_key': myRawCacheKey,
        }),
        contentType:'application/json',
        dataType: 'text',
        success: function(res){
            res = myParse(res);
            let new_sequence = res.new_sequence;
            $('#outputBlankSequences').val(new_sequence.name);
            newSequencesList.push(new_sequence);
        }
    })
}
function getInterpolatedBlank() {
    let names = document.getElementById('inputBlankSequences').value;
    let separator = names.includes(';') ? ';' : ' ';
    let nameList = names.split(separator);
    if (nameList.indexOf('') !== -1) {nameList.splice(nameList.indexOf(''), 1)}
    if (nameList.length === 0) {return}
    let blanksInfos;
    try {
        blanksInfos = nameList.map(function (name, index) {
            if (name !== '') {return getBlankInfo(name);}
        });
    } catch (e) {
        let text = "The blank sequences don't exist. Please check if a whitespace may be in the names and use a semicolon as a delimiter.";
        showPopupMessage('Information', text, false);
        return
    }
    let blank_data = blanksInfos.map(function (blank, index) {
        return [blank[0].time, blank[0].intercept, blank[1].intercept,
            blank[2].intercept, blank[3].intercept, blank[4].intercept];
    });

    // 通过DOM获取已存在的ECharts实例，若存在则销毁
    ['figure-main', 'figure-01', 'figure-02', 'figure-03', 'figure-04', 'figure-05'].forEach((div, index) => {
        const _ = echarts.getInstanceByDom(document.getElementById(div));
        if (_) {_.off('click');}
    })

    showModalDialog('modal-dialog-interpolate-blank');
    let charts = getLinkedChart('figure-main', 'figure-01', 'figure-02', 'figure-03', 'figure-04', 'figure-05');
    $.each(charts, function (index, each) {
        let scatter_data = [transpose(blank_data)[0], transpose(blank_data)[index===0?1:index]];
        // Note only consider unknown sequences and selected blank sequences
        let datetime_list = myRawData.sequence.filter((item, index) =>
            nameList.includes(item.name) || !item.is_blank).map((v, i) => v.datetime);
        let regression_results = {
            linear: getRegressionResults(scatter_data, 'linear', datetime_list),
            quadratic: getRegressionResults(scatter_data, 'quadratic', datetime_list),
            // polynomial: getRegressionResults(scatter_data, 'polynomial', datetime_list),
            exponential: getRegressionResults(scatter_data, 'exponential', datetime_list),
            // power: getRegressionResults(scatter_data, 'power', datetime_list),
            average: getRegressionResults(scatter_data, 'average', datetime_list),
        }
        each.setOption({
            title: {text: `${index===0?'Blank interpolation ':''}${['Ar36', 'Ar37', 'Ar38', 'Ar39', 'Ar40'][index===0?0:index-1]}`},
            yAxis: {
                name: index === 0?'Intensity (fA)':'', axisTick: {show: index === 0}, axisLabel: {show: index === 0},
            },
            xAxis: {
                name: index === 0?'Time':'', type: 'time', nameLocation: 'middle', nameGap: -20,
                nameTextStyle: {fontSize: 18, fontWeight: 'bold'},
                axisTick: {show: index === 0},
                axisLabel: {formatter: '{dd} {MMM} {HH}:{mm}:{ss}', rotate: 10, show: index === 0},
            },
            series: [
                {id: 'FilledPoints', encode: {x: 0, y: index===0?1:index}, data: blank_data},
                {id: 'UnfilledPoints', encode: {x: 0, y: index===0?1:index}, data: []},
                {id: 'LineRegression', data: transpose(regression_results.linear.step_data)},
                {id: 'QuadRegression', data: transpose(regression_results.quadratic.step_data)},
                // {id: 'PolyRegression', data: transpose(regression_results.polynomial.step_data)},
                {id: 'ExpRegression', data: transpose(regression_results.exponential.step_data)},
                // {id: 'PowRegression', data: transpose(regression_results.power.step_data)},
                {id: 'Average', data: transpose(regression_results.average.step_data)},
            ],
            graphic: [{
                id: 'LinesResults',
                style: {
                    font: '16px "", Consolas, monospace',
                    text: text_table([
                        ['', 'Standard Error of Estimate', 'R2'],
                        ['Linear', regression_results.linear.sey, regression_results.linear.r2],
                        ['Quadratic', regression_results.quadratic.sey, regression_results.quadratic.r2],
                        // ['Polynomial', regression_results.polynomial.sey, regression_results.polynomial.r2],
                        ['Exponential', regression_results.exponential.sey, regression_results.exponential.r2],
                        // ['Power', regression_results.power.sey, regression_results.power.r2],
                        ['Average', regression_results.average.sey, regression_results.average.r2],
                    ], {hsep: '  ', align: ['l', 'l', 'l'] })
                },
            }],
            animation: false,
        })
        each.resize();
    });

    $('#modal-dialog-interpolate-blank :button[name="apply"]').off('click').on('click', (event)=>{
        // 0 for linear, 1 for quadratic, 2 for polynomial, 3 for exponential, 4 for power, 5 for average
        let selects = $('#modal-dialog-interpolate-blank select[name="blankInterpolate"]');
        let interpolated_blank = Array(5);
        for (let isotope=0;isotope<5;isotope++){
            interpolated_blank[isotope] = getSeriesById(
                ['LineRegression', 'QuadRegression', 'PolyRegression', 'ExpRegression',
                    'PowRegression', 'Average'][selects.eq(isotope).val()],
                charts[isotope+1].getOption().series).data
            if (interpolated_blank[isotope].length !== 0) {continue;}
            let text = `Results unavailable, please select another fitting method for Ar${['36', '37', '38', '39', '40'][isotope]}!`;
            showPopupMessage('Information',text, false)
            return
        }

        interpolated_blank = transpose(interpolated_blank);
        let output_name = document.getElementById('outputBlankSequences').value;
        $.ajax({
            url: url_raw_interpolated_blanks,
            type: 'POST',
            data: JSON.stringify({
                'interpolated_blank': interpolated_blank,
                'new_blank_name': output_name,
                'cache_key': myRawCacheKey,
            }),
            contentType:'application/json',
            dataType: 'text',
            success: function(res){
                res = myParse(res);
                output_name = res.sequences[0].name
                if (Array.isArray(myRawData['interpolated_blank'])) {
                    myRawData['interpolated_blank'].push(...res.sequences)
                } else {
                    myRawData['interpolated_blank'] = res.sequences;
                }
                newSequencesList.push({
                    "index": "undefined",
                    "name": output_name,
                    "datetime": "",
                    "data": null,
                    "flag": null,
                    "type_str": "blank",
                    "results": [
                        [["Interpolated Blank", NaN, NaN, NaN]],
                        [["Interpolated Blank", NaN, NaN, NaN]],
                        [["Interpolated Blank", NaN, NaN, NaN]],
                        [["Interpolated Blank", NaN, NaN, NaN]],
                        [["Interpolated Blank", NaN, NaN, NaN]],
                    ],
                    "coefficients": [],
                    "fitting_method": [0, 0, 0, 0, 0],
                    "is_blank": true,
                    "is_unknown": false,
                    "is_estimated": true,
                })
                // Back to blank selection page
                // $('#outputBlankSequences').val("Interpolated Blank");
                $('#outputBlankSequences').val(output_name);
                showModalDialog('modal-dialog-blank');
            }
        });
    });
}
function getBlankInfo(item) {
    // blank sequence name
    let blank = myRawData.sequence.filter((seq, index) => seq.name === item)[0];
    return [
        blank.results[0][blank.fitting_method[0]], blank.results[1][blank.fitting_method[1]],
        blank.results[2][blank.fitting_method[2]], blank.results[3][blank.fitting_method[3]],
        blank.results[4][blank.fitting_method[4]]
    ].map(function (isotope, index){
        return {
            'isotope': ["Ar36", "Ar37", "Ar38", "Ar39", "Ar40"][index],
            'intercept': isotope[0], 'absolute err': isotope[1], 'relative err': isotope[2],
            'r2': isotope[3], 'time': blank.datetime, 'name': item,
        }
    })
}
function getCurrentIsotope() {
    for (let i=0;i<smCharts.length;i++){
        if (smCharts[i].getOption().series[0].color===FILLED_POINTS_COLOR){
            return i;
        }
    }
}
function getExtrapolateDefaultOption(){
    return {
        title: {text: '', subtext: '', left: 'center',
            textStyle: { fontSize: 18, fontWeight: 'bold',}},
        tooltip: {axisPointer: {type: 'none'}, confine: true, trigger: 'axis', showContent: false},
        legend: {show: true, top:'5%',
            data: [
                'Filled Points', 'Unfilled Points',
                'Line Regression', 'Quad Regression',
                // 'Poly Regression',
                'Exp Regression',
                // 'Pow Regression',
                'Average',
            ]},
        grid: {show: true, borderWidth: 1, borderColor: '#333', top: '5%', left: '5%', bottom: '5%', right: '5%'},
        xAxis: {name: '', type: 'value', nameLocation: 'middle', nameGap: -20,
            nameTextStyle: {fontSize: 18, fontWeight: 'bold'},
            axisLabel: {show: false},
            axisTick: {show: false},
            splitLine: {show: false},
            axisLine: {show: false, onZero: false}},
        yAxis: {name: '', type: 'value', scale: true, nameLocation: 'middle', nameGap: -25,
            nameTextStyle: {fontSize: 18, fontWeight: 'bold'},
            splitLine: {show: false},
            axisLabel: {show: false},
            axisTick: {show: false},
            axisLine: {show: false, onZero: false}},
        series: [
            {id: 'FilledPoints', name: 'Filled Points', type: 'scatter', color: '#222222', symbolSize: 10, data: [], z: 3},
            {id: 'UnfilledPoints', name: 'Unfilled Points', type: 'scatter', color: '#FFFFFF', symbolSize: 10, data: [], z: 3,
                itemStyle: {
                    normal: {borderColor: '#222222', borderWidth: 2}},},
            {id: 'LineRegression', name: 'Line Regression', type: 'line', color: '#5cb85c', clip: true, triggerLineEvent: false,
                lineStyle: {color: '#5cb85c'}, showSymbol: false, symbolSize: 0, data: [], z: 0},
            {id: 'QuadRegression', name: 'Quad Regression', type: 'line', color: '#d8c400', clip: true, triggerLineEvent: false,
                lineStyle: {color: '#d8c400'}, showSymbol: false, symbolSize: 0, data: [], z: 0},
            // {id: 'PolyRegression', name: 'Poly Regression', type: 'line', color: '#f0ad4e', clip: true, triggerLineEvent: false,
            //     lineStyle: {color: '#f0ad4e'}, showSymbol: false, symbolSize: 0, data: [], z: 0},
            {id: 'ExpRegression', name: 'Exp Regression', type: 'line', color: '#d9534f', clip: true, triggerLineEvent: false,
                lineStyle: {color: '#d9534f'}, showSymbol: false, symbolSize: 0, data: [], z: 0},
            // {id: 'PowRegression', name: 'Pow Regression', type: 'line', color: '#329ea8', clip: true, triggerLineEvent: false,
            //     lineStyle: {color: '#329ea8'}, showSymbol: false, symbolSize: 0, data: [], z: 0},
            {id: 'Average', name: 'Average', type: 'line', color: '#808080', clip: true, triggerLineEvent: false,
                lineStyle: {color: '#808080', type: 'dashed'}, showSymbol: false, symbolSize: 0, data: [], z: 0},
        ],
        graphic: [{
            id: 'LinesResults', type: 'text', z: 0, draggable: true, x: 300, y: 100,
            style: {fill: '#FF0000', overflow: 'break', font: '18px "", Consolas, monospace'},
        }]
    };
}
function getParamsByObjectName(type) {
    // type = 'irra' or 'calc' or 'smp' or 'input-filter' or 'thermo'
    let params = [];
    let inputs = document.getElementsByClassName(`${type}-params`);
    let checkBoxes = document.getElementsByClassName(`${type}-check-box`);
    $.each(inputs, function (index, each) {
        params.push(each.type === "number" ? each.valueAsNumber : each.value);
    });
    $.each(checkBoxes, function (index, each) {
        params.push(each.checked);
    });
    // console.log(params);
    return params;
}
function getLineData(allData, sequence, isotopes, type) {
    return allData[sequence-1][isotopes-1][type-1]
}
function getScatterData(allData, sequence, isotopes) {
    try {
        return allData[sequence-1][isotopes-1];
    } catch (e) {
        return []
    }
}
function initialTable(blankNameList) {
    // initialize sequence table
    $('#table-sequences').bootstrapTable(
        {
            clickToSelect: false,                //是否启用点击选中行
            uniqueId: "id",                     //每一行的唯一标识，一般为主键列
            columns: [
                {field: 'checked', checkbox: true, width: 20},
                {field: 'id', title: 'No.', width: 20,},
                {field: 'label', title: 'Label', width: 50,},
                {field: 'unknown', title: 'Unknown', width: 200,},
                {field: 'blank', title: 'Blank', width: 200,
                    formatter: function (value, row, index){
                        let option = "";
                        let num = index + 1;
                        $.each(blankNameList, function (i, item) {
                            option = option + "<option value='"+item+"'>"+item+"</option>";
                        })
                        return '<select id="blank-sele' + num + '" name="blankSelectinTable" onchange="blankSeleChanged(id)" style="width:100%; height: 100%; border: none; padding: 0 0 0 0">' + option + '</select>';
                    }
                }
            ]
        }
    );

    $('#table-blank-info').bootstrapTable(
    {
        clickToSelect: false,
        columns: [
            {field: 'isotope', title: 'Isotope', width: 20,},
            {field: 'intercept', title: 'Intercept', width: 150,},
            {field: 'absolute err', title: '1s', width: 150,},
            {field: 'relative err', title: '%1s', width: 150,},
            {field: 'r2', title: 'R2', width: 150,},
        ]
    })
}
function blankSeleChanged(id) {
    console.log(id);
}
function irradiationCyclesChanged(num) {
    let container = document.getElementById('irradiationTimeContainer');
    container.innerHTML = '';
    for (let i=0;i<num;i++){
        container.innerHTML = container.innerHTML + '<div class="form-inline">'+
            '<label style="width: 90px; text-align: left">End Time</label>'+
            '<label><input type="datetime-local" class="irra-params" style="width: 180px;"><label style="width: 80px; text-align: right">Duration </label>'+
            '<input type="number" class="irra-params" style="width: 60px;"> hour(s)</label></div>'
        }
}
function seqStateChanged() {
    let is_blank = $('#isBlank').is(':checked');
    let is_removed = $('#isRemoved').is(':checked');
    $.ajax({
        url: url_raw_change_seq_state,
        type: 'POST',
        data: JSON.stringify({
            'sequence_index': current_page - 1,
            'is_blank': is_blank,
            'is_removed': is_removed,
            'cache_key': myRawCacheKey}),
        processData : false,
        contentType : false,
        mimeType: "multipart/form-data",
        success: function(res){
            myRawData.sequence[current_page-1].is_blank = is_blank;
            myRawData.sequence[current_page-1].is_removed = is_removed;
        }
    })
}
function lastSequence() {
    if (current_page - 1 > 0){
        showSequence(current_page - 1);
    }
}
function nextSequence() {
    if (current_page + 1 <= max_page){
        showSequence(current_page + 1);
    }
}
function smchartOnClick(smCharts, bigChart, i) {
    smCharts[i].setOption({
        series: [
            {color: FILLED_POINTS_COLOR},
            {itemStyle: {normal: {borderColor: FILLED_POINTS_COLOR}}}]
    });
    for (let j=0;j<smCharts.length;j++) {
        if (j !== i) {
            smCharts[j].setOption({series: [{color: '#222'}, {itemStyle: {normal: {borderColor: '#222'}}}]})
        }
    }
    showSequence(current_page);
}
function setSmChartClickListen(smCharts, bigChart) {
    for (let i=0;i<smCharts.length;i++) {
        smCharts[i].getZr().on('click', function(event) {
            // 设置小图颜色
            smchartOnClick(smCharts, bigChart, i);
            // smCharts[i].setOption({
            //     series: [
            //         {color: FILLED_POINTS_COLOR},
            //         {itemStyle: {normal: {borderColor: FILLED_POINTS_COLOR}}}]});
            // for (let j=0;j<smCharts.length;j++) {
            //     if (j !== i) {smCharts[j].setOption({
            //         series: [{color: '#222'}, {itemStyle: {normal: {borderColor: '#222'}}}]})}
            // }
            // showSequence(current_page);
            // 没有 target 意味着鼠标/指针不在任何一个图形元素上，它是从“空白处”触发的。
            if (!event.target) {
                // 点击在了空白处，做些什么。
            }
        });
    }
    smCharts[0].setOption({
        series: [{color: FILLED_POINTS_COLOR}, {itemStyle: {normal: {borderColor: FILLED_POINTS_COLOR}}}]});
}
function showModal(id) {
    $('.modal:visible').modal('hide');
    $('#'+id).modal('show');
    // forEach($('.modal:visible'), (modal)=>{
    //     console.log(modal);
    //     console.log(modal.id);
    //     modal.removeAttribute('aria-hidden');
    // });
}
function showModalDialog(id) {
    $('.modal-dialog:visible').attr('hidden', true);
    $('#'+id).attr('hidden', false);
}
function showSequence(page) {  // page starts with 1
    let btns = document.getElementsByName('sequenceBtn');
    for (let i=0;i<btns.length;i++){
        if (i + 1 !== page && btns[i].className.includes("btn-warning")) {
            continue;
        }
        btns[i].className = 'btn btn-default btn-no-outline';
        if (myRawData.sequence[i].is_blank) {
            btns[i].className = 'btn btn-grey btn-no-outline';
        }
        if (myRawData.sequence[i].is_removed) {
            btns[i].className = 'btn btn-danger btn-no-outline';
        }
        if (btns[i].innerText === page.toString()){
            btns[i].className = 'btn btn-primary';
        }
    }
    current_page = page;
    $('#page_num').text(current_page + '/' + max_page);
    if (current_page === 1){
        $('#last_page').attr("disabled",true);
        $('#next_page').attr("disabled",false);
    } else if (current_page === max_page) {
        $('#next_page').attr("disabled",true);
        $('#last_page').attr("disabled",false);
    } else {
        $('#last_page').attr("disabled",false);
        $('#next_page').attr("disabled",false);
    }
    updateCharts(smCharts, chartBig, page-1, true, myRawData.sequence[page-1].fitting_method);
    $('#fitMethod').val(myRawData.sequence[page-1].fitting_method[getCurrentIsotope()]);
    $('#isBlank').prop("checked", myRawData.sequence[page-1].is_blank);
    $('#isRemoved').prop("checked", myRawData.sequence[page-1].is_removed);
    // console.log(chartBig.getOption());
}
function submitDelete() {
    $('#modal-delete').modal('show');
    $('#name3').val($('select[name="projectName"]:first').val());
}
function submitExtrapolate() {
    let unknown_sequence = myRawData.sequence.filter((seq, index) => !seq.is_blank);
    let blank_sequence = myRawData.sequence.filter((seq, index) => seq.is_blank);
    if (blank_sequence.length === 0) {
        $.ajax({
            url: url_raw_empty_blank,
            type: 'POST',
            data: JSON.stringify({
                'cache_key': myRawCacheKey,
            }),
            async: false,
            contentType:'application/json',
            success: function(res){
                let new_seq = myParse(res.new_sequence);
                // new_seq.index = 0;
                blank_sequence = [new_seq];
                myRawData.sequence.push(new_seq)
            }
        })
    }
    // 初始化表格+
    $('#table-sequences').bootstrapTable('destroy');
    initialTable(blank_sequence.filter(seq => !seq.is_removed).map((seq, index) => seq.name));
    updateSequenceTable();
    corrBlankMethodChanged(blank_sequence);
    // 初始化本底列表
    let li_list = document.getElementById('listGroupBlankName');
    while (li_list.hasChildNodes()){
        li_list.removeChild(li_list.lastChild)
    }
    let btn_list = document.getElementById('listGroupBlankBtn');
    while (btn_list.hasChildNodes()){
        btn_list.removeChild(btn_list.lastChild)
    }
    $.each(blank_sequence.map((seq, index) => seq.name), function (i, item) {
        addNametoBlankList(item);
    })
    showModal('modal-settings');

}
function submitOrSave() {
    if ($('#submitBtn').text() === 'Submit') {
        $('#modal-submit').modal('show');
    } else if ($('#submitBtn').text() === 'Save') {
        $('#modal-save').modal('show');
        $('#name2').val($('select[name="projectName"]:first').val());
    } else {
        
    }
}
function saveExportSettings() {
    $('#modal-save').modal('show');
    $('#name2').val($('select[name="projectName"]:first').val());
}
function getSelectedData(sequence_data, sequence_flag) {
    let selected = sequence_data.map(function (arr, i) {
        return arr.map(function (value, j) {
            return j === 0 ? value : sequence_flag[i][j]? value : NaN
        });
    });
    let unselected = sequence_data.map(function (arr, i) {
        return arr.map(function (value, j) {
            return j === 0 ? value : !sequence_flag[i][j]? value : NaN
        });
    });
    return [selected, unselected];
}
function generateLinesData(func, xmin=0, xmax=200, num=20) {
    let data = [];
    let step = (xmax - xmin) / num;
    for (let i = 0; i < num; i += 1) {
        data.push([xmin + i * step, func(xmin + i * step)]);
    }
    data.push([xmax, func(xmax)]);
    return data;
}
function updateCharts(smCharts, bigChart, sequence_index, animation, fitting_method) {
    let [selected, unselected] = getSelectedData(
        myRawData.sequence[sequence_index].data, myRawData.sequence[sequence_index].flag);
    let coeff = myRawData.sequence[sequence_index].coefficients;
    for (let i=0;i<smCharts.length;i++) {
        // smCharts length should be 5
        let xmax = Math.max(...selected.concat(unselected).map((value, index) => value[i * 2 + 1]).filter(value => !Number.isNaN(value)));
        let option = {
            xAxis: {min: 0, max: xmax},
            series: [
                {
                    name: 'Filled Points', data: selected, encode: {x: i * 2 + 1, y: i * 2 + 2},
                    label: {show: false, position: 'top', formatter: (params) => params.dataIndex + 1},
                },
                {
                    name: 'Unfilled Points', data: unselected, encode: {x: i * 2 + 1, y: i * 2 + 2},
                    label: {show: false, position: 'top', formatter: (params) => params.dataIndex + 1},
                },
                {
                    name: 'Line Regression', tooltip: {formatter: 'Linear'}, data: generateLinesData(
                    (x) => coeff[i][0][0] + x * coeff[i][0][1], 0, xmax, 1),
                    lineStyle: {width: fitting_method[i]===0?5:2},
                },
                {
                    name: 'Quad Regression', tooltip: {formatter: 'Quadratic'}, data: generateLinesData(
                    (x) => coeff[i][1][0] + x * coeff[i][1][1] + x * x * coeff[i][1][2], 0, xmax),
                    lineStyle: {width: fitting_method[i]===1?5:2},
                },
                {
                    name: 'Exp Regression', tooltip: {formatter: 'Exponential'}, data: generateLinesData(
                    // y = a + exp(b * x) + c 2025-12-07
                    (x) => coeff[i][2][0] * Math.exp(coeff[i][2][1] * x) + coeff[i][2][2], 0, xmax),
                    lineStyle: {width: fitting_method[i]===2?5:2},
                },
                // {name: 'Pow Regression', tooltip: {formatter: 'Power'}, data: generateLinesData(
                //     (x) => coeff[i][3][0] * x ** coeff[i][3][1] + coeff[i][3][2], 0, xmax),
                //     lineStyle: {width: fitting_method[i]===3?5:2},
                // },
                {
                    name: 'Average', tooltip: {formatter: 'Average'}, data: generateLinesData(
                    (x) => coeff[i][4][0], 0, xmax, 1),
                    lineStyle: {width: fitting_method[i]===4?5:2},
                },
            ],
            animation: animation,
        };
        smCharts[i].setOption(option);
        if (smCharts[i].getOption().series[0].color === FILLED_POINTS_COLOR) {
            let res = myRawData.sequence[sequence_index].results[i]
            let parseRes = (res) => {
                return [typeof res[0] === 'number'?res[0].toFixed(5):res[0], res[1].toFixed(5), isFinite(res[2])?res[2].toFixed(3)+'%':res[2], res[3].toFixed(5)]
            }
            bigChart.setOption(option);
            let text = [
                ['', 'Intercept', 'SE', 'RSE', 'R2'],
                ['Linear'].concat(parseRes(res[0])),
                ['Quadratic'].concat(parseRes(res[1])),
                ['Exponential'].concat(parseRes(res[2])),
                // ['Power'].concat(parseRes(res[3])),
                ['Average'].concat(parseRes(res[4]))
            ];
            bigChart.setOption({
                title: {text: `${myRawData.sequence[sequence_index].name}  ${myRawData.sequence[sequence_index].datetime}  ${['Ar36', 'Ar37', 'Ar38', 'Ar39', 'Ar40'][i]} ${myRawData.sequence[sequence_index].type_str} ${myRawData.sequence[sequence_index].label}`},
                graphic: [{
                    id: 'LinesResults', type: 'text', z: 0, draggable: true,
                    style: {fill: '#FF0000', overflow: 'break', text: text_table(text), font: '18px "", Consolas, monospace'},
                }]
            })
        }
    }
}
function updateSequenceTable() {
    let tableData = [];
    let unknown_sequence = myRawData.sequence.filter((seq, index) => !seq.is_blank);
    for (let i=0; i<unknown_sequence.length; i++){
        tableData.push({
            'checked': !unknown_sequence[i].is_removed, 'id': i+1,
            // 'unknown': unknown_sequence[i].name, 'label': unknown_sequence[i].type_str
            'unknown': unknown_sequence[i].name, 'label': unknown_sequence[i].label
        });
    }
    $('#table-sequences').bootstrapTable('load', tableData);
}
function paramsRadioChanged(flag, callback=null) {
    flag = flag.value? flag.value : flag;
    // flag = 'irra', 'calc', 'smp'
    let inputs = $(`#${flag}ParamsInputForm`).find($('input'));
    if ($(`#${flag}ParamsRadio1`).is(':checked')) {
        showParamProject(document.getElementById(`${flag}ProjectName`), flag, true, callback);
        $(`#${flag}ParamsInputForm`).find($('select,input[type="checkbox"],input[type="radio"]')).attr('disabled', true);
        inputs.css('background-color', '#eee');
        inputs.css('border-color', '#ccc');
        inputs.attr('readOnly', true);
    } else {
        $(`#${flag}ParamsInputForm`).find($('select,input[type="checkbox"],input[type="radio"]')).attr('disabled', false);
        inputs.css('background-color', '#fff');
        inputs.removeAttr('border-color');
        inputs.attr('readOnly', false);
    }
    if (flag === 'smp'){initialRatioSelectChanged()}
}
// packaging a function to create echart instance (to be completed)
// function getEchart(dom, option) {
//     if (!option) option = {};
//     let chart = echarts.init(dom, null, {renderer: 'svg'});
//     chart.setOption({
//         title: {text: '', subtext: '', left: 'center', textStyle: { fontSize: 18, fontWeight: 'bold',}},
//         tooltip: {axisPointer: {type: 'none'}, confine: true, trigger: 'axis', showContent: false},
//         legend: {show: false, top:'5%',},
//         grid: {show: true, borderWidth: 1, borderColor: '#333', top: '5%', left: '5%', bottom: '5%', right: '5%'},
//         xAxis: {
//             name: '', type: 'value', nameLocation: 'middle', nameGap: -20,
//             nameTextStyle: {fontSize: 18, fontWeight: 'bold'},
//             axisLabel: {show: false}, axisTick: {show: false}, splitLine: {show: false}, axisLine: {show: false, onZero: false}},
//         yAxis: {
//             name: '', type: 'value', scale: true, nameLocation: 'middle', nameGap: -25,
//             nameTextStyle: {fontSize: 18, fontWeight: 'bold'},
//             splitLine: {show: false}, axisLabel: {show: false}, axisTick: {show: false}, axisLine: {show: false, onZero: false}},
//         series: [
//             {name: 'Filled Points', type: 'scatter', color: '#222222', symbolSize: 10, data: [], z: 2},
//             {name: 'Unfilled Points', type: 'scatter', color: '#FFFFFF', symbolSize: 10, data: [], z: 2,
//                 itemStyle: {normal: {borderColor: '#222222', borderWidth: 2}},
//             },
//         ]
//     });
//
//      let scatterClicked = (params) => {
//         let scatterIndex = params.dataIndex;
//         let scatterValue = params.data;
//         let scatterIsFilled = !params.seriesName.includes('Unfilled'); // true for filled scatter
//         let option = chart.getOption();
//         let filledData = option.series[0].data;
//         let unfilledData = option.series[1].data;
//         if (scatterIsFilled) {
//             filledData.splice(scatterIndex, 1);
//             unfilledData.push(scatterValue);
//         } else {
//             unfilledData.splice(scatterIndex, 1);
//             filledData.push(scatterValue);
//         }
//         // doing other things there
//     }
//
//     // listen click on scatters
//     chart.on('click', 'series.scatter', function (params) {scatterClicked(params)});
//
//     return chart
//
//
// }
function getSeriesById(id, opts) {
    if (!opts) opts = [{id:''}];
    return opts[opts.findIndex((element) => element.id === id)]
}
function getLinkedChart(mainDiv, ...divs) {
    let chartMain = echarts.init(document.getElementById(mainDiv), null, {renderer: 'svg'});
    let chartSmall = divs.map((div, index)=>{
        let chart = echarts.init(document.getElementById(div), null, {renderer: 'svg'});
        chart.setOption(getExtrapolateDefaultOption());
        chart.setOption({
            title: {left: '5%', top:'5%', textStyle: {fontSize: 12, fontWeight: 'normal'}}, legend: {show: false},
            graphic: [{
                id: 'LinesResults', invisible: true, type: 'text', draggable: true,
                style: {fill: '#FF0000', overflow: 'break', font: '16px "", Consolas, monospace', text: ''},
            }],
        });
        return chart
    });
    let smallChartClicked = (index, chart = null) => {
        chart === null ? chart = chartSmall[index] : chart
        // Setting big figure based on the clicked small figure
        let option = chart.getOption();
        let series = option.series;
        // console.log(option);
        // console.log("small charts clicked.");
        chartMain.setOption({
            title: {text: `Blank interpolation ${option.title[0].text}`},
            series: series.map((_item, _index) => {
                let isLine = !_item.name.includes('Points');
                return {
                    id: _item.id, data: _item.data, encode: _item.encode,
                    symbolSize: isLine?5:10,
                    symbol: isLine?'emptyrect':'circle',
                    showSymbol: true,
                }
            }),
            graphic: [{
                id: 'LinesResults', invisible: false, type: 'text', draggable: true,
                style: {
                    fill: '#FF0000', overflow: 'break',
                    // Using monospaced font and spaces to align text
                    font: '16px "", Consolas, monospace',
                    text: option.graphic[0].elements?.[0].style.text,
                },
            }]
        });

        // 设置小图颜色
        for (let j=0;j<chartSmall.length;j++) {
            chartSmall[j].setOption({
                series: [
                    {id: 'FilledPoints', color: j !== index?'#222222':FILLED_POINTS_COLOR},
                    {id: 'UnfilledPoints', itemStyle: {normal: {borderColor: j !== index?'#222222':FILLED_POINTS_COLOR}}}]
            })
        }

        //切换拟合方式显示
        let selects = $('#modal-dialog-interpolate-blank select[name="blankInterpolate"]');
        selects.attr('style', (_index, attr) => {
            return _index === index ? "" : "display: none";
        });
    }
    let scatterClicked = (params) => {
        let chartIndex = params.encode.y[0] - 1;
        let scatterIndex = params.dataIndex;
        let scatterValue = params.data;
        let scatterIsFilled = !params.seriesName.includes('Unfilled'); // true for filled scatter
        let option = chartSmall[chartIndex].getOption();
        let filledData = getSeriesById('FilledPoints', option.series).data;
        let unfilledData = getSeriesById('UnfilledPoints', option.series).data;
        if (scatterIsFilled) {
            filledData.splice(scatterIndex, 1);
            unfilledData.push(scatterValue);
        } else {
            unfilledData.splice(scatterIndex, 1);
            filledData.push(scatterValue);
        }
        let scatterData = [transpose(filledData)[params.encode.x[0]], transpose(filledData)[params.encode.y[0]]];
        // let datetime_list = myRawData.sequence.map((v, i) => v.datetime);
        let names = document.getElementById('inputBlankSequences').value;
        let separator = names.includes(';') ? ';' : ' ';
        let nameList = names.split(separator);
        if (nameList.indexOf('') !== -1) {nameList.splice(nameList.indexOf(''), 1)}
        if (nameList.length === 0) {return}
        let datetime_list = myRawData.sequence.filter((item, index) =>
            nameList.includes(item.name) || !item.is_blank).map((v, i) => v.datetime);
        let regressionResults = {
            linear: getRegressionResults(scatterData, 'linear', datetime_list),
            quadratic: getRegressionResults(scatterData, 'quadratic', datetime_list),
            // polynomial: getRegressionResults(scatterData, 'polynomial', datetime_list),
            exponential: getRegressionResults(scatterData, 'exponential', datetime_list),
            // power: getRegressionResults(scatterData, 'power', datetime_list),
            average: getRegressionResults(scatterData, 'average', datetime_list),
        }
        chartSmall[chartIndex].setOption({
            series: [
                {id: 'FilledPoints', encode: getSeriesById('FilledPoints', option.series).encode, data: filledData},
                {id: 'UnfilledPoints', encode: getSeriesById('UnfilledPoints', option.series).encode, data: unfilledData},
                {id: 'LineRegression', data: transpose(regressionResults.linear.step_data)},
                {id: 'QuadRegression', data: transpose(regressionResults.quadratic.step_data)},
                // {id: 'PolyRegression', data: transpose(regressionResults.polynomial.step_data)},
                {id: 'ExpRegression', data: transpose(regressionResults.exponential.step_data)},
                // {id: 'PowRegression', data: transpose(regressionResults.power.step_data)},
                {id: 'Average', data: transpose(regressionResults.average.step_data)},
            ],
            graphic: [{
                id: 'LinesResults', invisible: true, type: 'text',
                style: {
                    fill: '#FF0000', overflow: 'break', font: '16px "", Consolas, monospace',
                    text: text_table([
                        ['', 'Regression Standard Error', 'R2'],
                        ['Linear', regressionResults.linear.sey, regressionResults.linear.r2],
                        ['Quadratic', regressionResults.quadratic.sey, regressionResults.quadratic.r2],
                        // ['Polynomial', regressionResults.polynomial.sey, regressionResults.polynomial.r2],
                        ['Exponential', regressionResults.exponential.sey, regressionResults.exponential.r2],
                        // ['Power', regressionResults.power.sey, regressionResults.power.r2],
                        ['Average', regressionResults.average.sey, regressionResults.average.r2],
                    ], {hsep: '  ', align: ['l', 'l', 'l'] })
                },
            }],
        })

        // 刷新大图
        smallChartClicked(chartIndex, chartSmall[chartIndex])

    }
    chartMain.setOption(getExtrapolateDefaultOption());
    // Listen click on small charts
    $.each(chartSmall, (index, chart)=>{
        chart.getZr().on('click', function(event) {
            smallChartClicked(index, chart);
            // 没有 target 意味着鼠标/指针不在任何一个图形元素上，它是从“空白处”触发的。
            if (!event.target) {
                // 点击在了空白处，做些什么。
            }
        });
        // Listen click on scatters
        chart.on('click', 'series.scatter', function (params) {scatterClicked(params)});
    })
    // listen click on scatters
    chartMain.on('click', 'series.scatter', function (params) {scatterClicked(params)});
    // Click the first small chart as default
    smallChartClicked(0);
    return [chartMain, ...chartSmall]
}
function getRegressionResults(data, method, x) {
    let result = {r2: 'None', sey: 'None', line_data: [], step_data: []};
    $.ajax({
        url: url_get_regression_result,
        type: 'POST',
        data: JSON.stringify({
            'data': data,
            'method': method,
            'x': x,
        }),
        async : false,
        contentType:'application/json',
        success: function(res){
            result = res;
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    })
    return result;
}

// object-functions
// drarmstr's answer
// https://stackoverflow.com/questions/18815197/javascript-file-dropping-and-reading-directories-asynchronous-recursion
function traverseDirectory(entry) {
    let reader = entry.createReader();
    // Resolved when the entire directory is traversed
    return new Promise((resolve_directory, reject) => {
        var iteration_attempts = [];
        (function read_entries() {
            // According to the FileSystem API spec, readEntries() must be called until
            // it calls the callback with an empty array.  Seriously??
            reader.readEntries((entries) => {
                if (!entries.length) {
                    // Done iterating this particular directory
                    resolve_directory(Promise.all(iteration_attempts));
                } else {
                    // Add a list of promises for each directory entry.  If the entry is itself
                    // a directory, then that promise won't resolve until it is fully traversed.
                    iteration_attempts.push(Promise.all(entries.map((entry) => {
                        if (entry.isFile) {
                            // DO SOMETHING WITH FILES
                            // return entry;
                            return new Promise((resolve, reject) => (entry.file(resolve, reject)));
                        } else {
                            // DO SOMETHING WITH DIRECTORIES
                            return traverseDirectory(entry);
                        }
                    })));
                    // Try calling readEntries() again for the same dir, according to spec
                    read_entries();
                }
            }, reject);
        })();
    });
}
function dropHandler(ev) {
    // Prevent default behavior (Prevent file from being opened)
    // Handle drag and drop events
    ev.preventDefault();
    let files = [];
    let directory_entry = [];
    if (ev.dataTransfer.items) {
        // Use DataTransferItemList interface to access the file(s)
        for (let item of [...ev.dataTransfer.items]){
            if (item.kind === "file") {
                let file = item.getAsFile();
                let entry = item.webkitGetAsEntry();
                if (entry.isDirectory) {
                    directory_entry.push(entry);
                } else {files.push(file);}
            }
        }
    }
    let formData = new FormData();
    let num_file = 0;
    let getFileFormdata = (_) => {
        if (_.constructor === Array) {
            _.forEach((__, i) => (getFileFormdata(__)));
        } else {
            formData.append(`${num_file}`, _);
            num_file += 1;
        }
    }
    let send_erquest = () => {
        for (let i=0;i<files.length;i++) {
             // Ignoring files bigger than about 20 MB
            if (files[i].size > 20 * 1024 * 1024 ) {
                showPopupMessage('Error', `The amount of data is too large (${(files[i].size / 1024 / 1024).toFixed(2)} MB), not supported.`, true)
                continue;
            }
            let flag = ''
            let file_input_id = ''
            let suffix = files[i].name.split('.').at(-1);
            switch (suffix) {
                case 'arr':
                    flag = `open_${suffix}_file`;
                    file_input_id = 'file-input-2';
                    break
                case 'xls':
                    flag = 'open_full_xls_file';
                    file_input_id = 'file-input-3';
                    break
                case 'age':
                    flag = `open_${suffix}_file`;
                    file_input_id = 'file-input-4';
                    break
                default:
                    showPopupMessage('Error', `Unknown ${suffix} file, not supported.`, true)
                    continue;
            }

            let file_input = null;
            let datatransfer = new DataTransfer();
            let trigger = (doc) => {
                doc.getElementById('button_index').value = flag
                file_input = doc.getElementById(file_input_id);
                datatransfer.items.add(files[i]);
                file_input.files = datatransfer.files;
                doc.getElementById('file-submit').click();
            }
            if (files.length===1) {
                trigger(document);
            } else {
                let newWindow = window.open(url_calc_view);
                // The page is from the same origin, so no security restriction.
                // onload is required because it takes a moment for the page to get loaded in the new window.
                newWindow.onload = () => {
                    trigger(newWindow.document);
                }
            }
        }

        // // Test for multi files request
        // // document.getElementById('button_index').value = "open_multi_files";
        // getFileFormdata(files);
        // formData.append('length', files.length.toString());
        // formData.append('flag', "open_multi_files");
        // $.ajax({
        //     url: url_calc_view,
        //     type: 'POST',
        //     data: formData,
        //     processData : false,
        //     contentType : false,
        //     mimeType: "multipart/form-data",
        //     success: function(res){
        //         console.log("Multi files have been uploaded");
        //     }
        // })
    }
    if (directory_entry.length === 0) {
        send_erquest();
    } else {
        if (directory_entry.length > 1) {
            showPopupMessage("Error", "Only one directory on the top level is supported.", true);
        }
        traverseDirectory(directory_entry[0]).then((files_promise)=> {
            // AT THIS POINT THE DIRECTORY SHOULD BE FULLY TRAVERSED.
            Promise.all(files_promise[0]).then((res) => {
                files.push(...res);
                send_erquest();
            });
        });
    }
}
function dragOverHandler(ev) {
  // console.log("File(s) in drop zone");
  // Prevent default behavior (Prevent file from being opened)
  ev.preventDefault();
}
function extendData(data) {
    // 补充数据形式以匹配表格大小
    let res = JSON.parse(JSON.stringify(data));
    for (let i = res.length; i < default_row_count; i++) {
        res.push([null]);
    }
    return res;
}
function clickExportBtn() {
    let export_type = document.getElementById('exportChoicesLabel').selectedIndex;
    // 0-Xls, 1-Opju, 2-single pdf, 3-merged pdf, 4-svg
    switch (export_type) {
        case 0:
            exportSmp(url_export_xls);
            break
        case 1:
            // exportSmp(url_export_opju);
            exportSmp(url_export_pdf, true, false);
            break
        // case 2: case 3:
        //     exportSmp(url_export_pdf, true, export_type === 3);
        //     break
        case 2:
            saveChart(true);
            break
        default:
            break
    }
}
function exportSmp(url, download=true, merged_pdf=false) {
    $.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify({
            'cache_key': cache_key,
            'figure_id': getCurrentTableId(),
            'merged_pdf': merged_pdf,
        }),
        contentType: 'application/json',
        beforeSend: function(){
            if (download) {
                // showMessage();
                showPopupMessage("Information", "Exporting, this may take a few moments, please wait...", false, false, 300000)
            }
        },
        success: function (res) {
            if (res.href.includes('arr')) {
                document.getElementById("download-arr").href = res.href;
                document.getElementById("download-arr").innerText = res.href.toString().split('/').slice(-1)[0];
            }
            if (download) {
                closePopupMessage();
                showPopupMessage("Information", "Exporting successfully. Starting download.", false)
                // showMessage(, 1000);
                document.getElementById("export_path_link").href = res.href;
                document.getElementById("export_path_link").click();
                setConsoleText('Export Successfully! ' + res.href);
            }
            document.getElementById("export_path_link").href = '';
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    });
}
function arrDownloaded() {
    rightConsole.innerText = `Last Download: ${getTime()}`;
}
async function saveChart(isExport=true) {
    let export_type = 'svg';
    if (getCurrentTableId() === 'figure_7') {
        // setConsoleText('3D plot cannot be exported or copied currently');
        export_type = 'png';
    }
    let svgBase64 = chart.getDataURL({type: export_type});
    let a = document.getElementById("export_path_link");
    let file_name = sampleComponents['0'].experiment.name+' '+$('#'+getCurrentTableId()).val()+".svg"
    if (isExport){
        if (getCurrentTableId() === 'figure_7') {
            setConsoleText('3D plot cannot be exported currently');
            return;
        }
        a.href = svgBase64;
        a.setAttribute("download",file_name); // Added file name
        a.click();
        a.setAttribute("download",''); // Clear download name
    } else {
        let image = new Image();
        image.src = svgBase64;
        image.onload = () => {
            let imageBase64;
            // Convert svg to png and then copy it to clipboard
            // https://blog.csdn.net/qq_36247432/article/details/119350921
            if (getCurrentTableId() === 'figure_7') {
                let png = document.getElementsByTagName('canvas')[0];
                imageBase64 = png.toDataURL('image/png');
            } else {
                let svg = document.getElementsByTagName('svg')[0];
                let width = svg.getAttribute('width');
                let height = svg.getAttribute('height');
                let canvas = document.createElement("canvas");
                let context = canvas.getContext('2d');
                canvas.setAttribute('width', width)
                canvas.setAttribute('height', height)
                context.drawImage(image, 0, 0, width, height );
                imageBase64 = canvas.toDataURL('image/png');
            }
            let b64data = imageBase64.split('base64,')[1]
            // Create blod based on image base64 string
            // https://stackoverflow.com/questions/16245767/creating-a-blob-from-a-base64-string-in-javascript
            let byteCharacters = atob(b64data);
            let byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            let byteArray = new Uint8Array(byteNumbers);
            let blob = new Blob([byteArray], {type: 'image/png'});
            // Write it to clipboard
            navigator.clipboard.write([new ClipboardItem({[blob.type]: blob})]);
            setConsoleText('Current figure has been copied to clipboard!')
        };

        // $.ajax({
        //     url: url_export_pdf,
        //     type: 'POST',
        //     data: JSON.stringify({'cache_key': cache_key,}),
        //     contentType: 'application/json',
        //     success: function (res) {},
        // });
        //
        // let items = await navigator.clipboard.read();
        // let textBlob = await items[0].getType("text/plain");
        // console.log(items[0].types);
        // let text = await (new Response(textBlob)).text();
        // console.log(text);
    }
}
function initialRatioSelectChanged() {
    let inputs = $('.input-initial-ratio');
    let disabled = $('#initialRatioSelect').val()!=='2';
    inputs.prop('disabled', disabled);
    inputs.css('background-color', disabled?'#eee':'#fff');
}
function clickPoints(params) {

    const current_set = isochronLine1Btn.checked ? 1 : 2;
    const current_figure = getCurrentTableId();
    const clicked_index = params.data.slice(-1)[0];  // should start from 0
    let all_figures = ['figure_2', 'figure_3', 'figure_4', 'figure_5', 'figure_6', 'figure_7'];

    chart.off('click', chart_on_clicked);
    let postData = JSON.stringify({ 'cache_key': cache_key,
        'content': {'clicked_index': [clicked_index], 'current_set': current_set,
            'auto_replot': true, 'figures': [current_figure], }
    });

    sendWebSocket('ws_click_chart', postData, onopen, onprogress, onclose, onerror, onfinish);

    function onopen(event) {
        let message = `Clicked：${params.seriesName}, Set${current_set}, Label: ${clicked_index+1}`;
        setConsoleText(message);
    }

    function onprogress(data) {
        if (data.res !== undefined) {
            sampleComponents = assignDiff(sampleComponents, data.res);
        }
        if (data.refresh) {
            showPage(current_figure, true);
        }
        setConsoleText(data.info);
    }

    function onclose(event) {
        chart.on('click', chart_on_clicked);
    }

    function onerror(data) {
        if (data.error !== undefined) {
            showPage(getCurrentTableId(), true);
            closePopupMessage();
            setConsoleText('Recalculation completed!');
            showPopupMessage("Error", data.error, true);
        }
    }

    function onfinish(data) {
        if (data.res !== undefined) {
            sampleComponents = assignDiff(sampleComponents, data.res);
            showPage(getCurrentTableId(), true);
            setConsoleText(data.info);
        }
        chart.on('click', chart_on_clicked);
    }

}
function getSetById(figure_id, set_id) {
    for (let [key, obj] of Object.entries(sampleComponents[figure_id])) {
        if (typeof obj === 'object' && obj !== null){
            if (obj.hasOwnProperty('id') && obj.id === set_id) {
                return obj
            }
        }
    }
}
function apply3DSetting() {
    let current_component = $('.setting-dialog:visible').attr('id');
    let figure = sampleComponents[getCurrentTableId()];
    if (current_component==='3Daxis-setting-in-dialog'){
        let xMax = document.getElementsByName('3d_xMax')[0].value;
        let xMin = document.getElementsByName('3d_xMin')[0].value;
        let yMax = document.getElementsByName('3d_yMax')[0].value;
        let yMin = document.getElementsByName('3d_yMin')[0].value;
        let zMax = document.getElementsByName('3d_zMax')[0].value;
        let zMin = document.getElementsByName('3d_zMin')[0].value;
        figure.xaxis.max = xMax;
        figure.xaxis.min = xMin;
        figure.yaxis.max = yMax;
        figure.yaxis.min = yMin;
        figure.zaxis.max = zMax;
        figure.zaxis.min = zMin;
        showPage(getCurrentTableId());
    }
}
async function clickSaveTable() {
    let table_data;
    let input_type = document.getElementById("inputSmpType");
    if (getCurrentTableId() === "0"){
        table_data = {
            "experiment": {
                "name": $('#inputExpName').val(), "type": $('#inputExpType').val()
            },
            "sample": {
                "name": $('#inputSmpName').val(), "type": $("#inputSmpType option:selected").text(),
                "material": $('#inputMaterial').val(), "location": $('#inputLocation').val()
            },
            "researcher" : {"name": $('#inputResearcher').val(),},
            "laboratory": {
                "name": $('#inputLaboratory').val(), "info": $('#inputLaboratoryMore').val(),
                "analyst": $('#inputAnalyst').val()
            }
        }
    } else {
        let table = sampleComponents[getCurrentTableId()];
        table_data = hot.getSourceData().map((row) => row.map((col, index) => col = table.header[index].includes("σ") ? col / confidence_level : col));
        // console.log(table_data);
        if (rows_to_delete.length > 0) {
            await showPopupMessage("Please confirm ...",
                `The following rows will be deleted: ${rows_to_delete.map(v => v + 1)}`, true).then((res) => {
                    if (!res) {return}
                    for (let table_id of ["1", "2", "3", "4", "5", "6", "7", "8"]) {
                        if (table_id === getCurrentTableId()) {
                            sampleComponents[table_id].data = table_data.filter((v, i) => v.length > 1);
                            continue;
                        }
                        sampleComponents[table_id].data = sampleComponents[table_id].data.filter(
                            (v, i) => ! rows_to_delete.includes(i) && v.length > 1);
                    }
                    sampleComponents[0].experiment.step_num = sampleComponents[0].experiment?.step_num - rows_to_delete.length;
                    rows_to_delete = [];
                    const diff = findDiff(sampleComponentsBackup, sampleComponents);
                    $.ajax({
                        url: url_update_components_diff,
                        type: 'POST',
                        data: JSON.stringify({
                            'diff': diff,
                            'cache_key': cache_key,
                        }),
                        contentType:'application/json',
                        success: function(res){
                            sampleComponentsBackup = JSON.parse(JSON.stringify(sampleComponents));
                            showPopupMessage("Information", "Successfully saved!", false);
                            setConsoleText('Changes Saved');
                        }
                    });
                });
            return;
        }
    }

    $.ajax({
        url: url_update_handsontable,
        type: 'POST',
        async: false,
        data: JSON.stringify({
            'btn_id': getCurrentTableId(),
            'recalculate': false,
            'cache_key': cache_key,
            'data': table_data,
            'rows_to_delete': rows_to_delete,
        }),
        contentType:'application/json',
        beforeSend: function(){
            showPopupMessage("Information", "Saving, please wait...", false, false,300000);
        },
        success: function(res){
            let changed_components = myParse(res.changed_components);
            assignDiff(sampleComponents, changed_components);
            if (getCurrentTableId() === "0"){$('#exp_name_title').text($('#inputExpName').val())}
            isochron_marks_changed = false;
            showPopupMessage("Information", "Successfully saved!", false);
            setConsoleText('Changes Saved');
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    });
}
function clickShowParams(flag) {
    let options;
    for (let i=0;i<=sampleComponents[0].experiment?.step_num;i++){
        let opt = i === 0 ? "All" : i.toString();
        options = options + `<option value=${opt}${$(`#${flag}RowNum`).val() === opt?' selected':''}>${opt}</option>`;
    }
    $(`#${flag}RowNum`).find('option').remove().end().append(options);
    $(`#${flag}ParamsRadio1`).prop("checked", false);
    $(`#${flag}ParamsRadio2`).prop("checked", true);
    $(`#${flag}RowNumRadio2`).prop("checked", true);
    paramsRadioChanged(flag);
    showParamProject(document.getElementById(`${flag}RowNum`), flag, false);
    $(`#edit${flag.charAt(0).toUpperCase() + flag.slice(1)}Params`).modal('show');
}
function clickForceSyn() {
    $.ajax({
        url: url_force_syn,
        type: 'POST',
        data: JSON.stringify({ 'cache_key': cache_key, }),
        contentType:'application/json',
        success: async function(response){
            sampleComponents = myParse(response.sampleComponents);
            showPage(getCurrentTableId(), true);
            showPopupMessage('Information', 'Forcing syn completed!', true)
            setConsoleText('Forcing syn completed!');
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    });
}
function clickRecalc() {
    const checked_options = $recalcCheckboxes.map(function() {
        return this.checked;
    }).get();
    $.ajax({
        url: url_recalculation,
        type: 'POST',
        data: JSON.stringify({
            'cache_key': cache_key,
            // 'checked_options': checked_options,
            'content': { 'checked_options': checked_options }
        }),
        contentType:'application/json',
        beforeSend: function(){
            if (checked_options[11]) {
                showPopupMessage("Information", "Using Monte Carlo simulation, this may take a few minutes depending on the number of sequences involved, please wait...", false, false, 300000);
            } else {
                showPopupMessage("Information", "Recalculation starts, please wait...", false, false,300000);
            }
        },
        success: async function(response){
            $('#promptModal').remove();
            await delay(500);
            let results = myParse(response.res);
            sampleComponents = assignDiff(sampleComponents, results);
            showPage(getCurrentTableId(), true);
            closePopupMessage();
            showPopupMessage('Information', 'Recalculation was successfully finished!', true)
            setConsoleText('Recalculation was successful');
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    });
}
function clickUploadPicture() {
    let file_input = $('#sample_photo_input');
    file_input.val("");
    file_input.click();
    file_input.change(function(){
        let fd = new FormData();
        fd.append('picture', $('#sample_photo_input')[0].files[0]);
        $.ajax({
            url: url_update_sample_photo,
            // url: url_calc_open_object,
            type: 'POST',
            processData: false,
            cache: false,
            contentType: false,
            data: fd,
            success: function(res){
                document.getElementById('sample_picture').setAttribute('src', res.picture);
                showUploadPictureBtn();
            }
        });
    });
}
function getCurrentTableId() {
    let tables = document.getElementsByName('table_name')
    for (let i=0; i<tables.length;i++){
        if (tables[i].classList.contains('active')){
            return tables[i].id
        }
    }
}
function getTime() {
    let date =  new Date();
    let month = date.getMonth() + 1;
    return date.getFullYear() + "/" + month + "/" + date.getDate() + "/ " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds()
}
function parseRowNumStr(str) {
    let arr = [];
    if (/^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$/.test(str)) {
        if (Number(str) > 0) {
            arr.push(Number(str));
        }
    }
    if (str.includes(';')) {
        str.split(';').forEach((_v, _i) => {
            parseRowNumStr(_v).forEach((each) => arr.push(each));
        })
    }
    else if (str.includes('；')) {
        str.split('；').forEach((_v, _i) => {
            parseRowNumStr(_v).forEach((each) => arr.push(each));
        })
    }
    else if (str.includes('-')) {
        let s = Number(str.split('-')[0]);
        let e = Number(str.split('-')[1]);
        for (let i=Math.max(Math.min(s, e), 1);i<=Math.max(s, e);i++) {
            arr.push(i);
        }
    }
    return arr
}
function readParams(type) {
    let apply_to_all = $(`#${type}RowNumRadio2`).is(':checked');
    let str = $(`#${type}RowNumTextInput`).val();
    let sel = $(`#${type}RowNumSelect`).val();
    let rows = apply_to_all ? parseRowNumStr(`1-${sampleComponents[0].experiment?.step_num}`) : str==="" ? parseRowNumStr(sel) : parseRowNumStr(str);
    $.ajax({
        url: url_set_params,
        type: 'POST',
        data: JSON.stringify({
            'params': getParamsByObjectName(type),
            'type': type,
            'rows': rows,
            'cache_key': cache_key,
        }),
        contentType:'application/json',
        success: function(res){
            let changed_components = myParse(res.changed_components);
            // console.log(changed_components);
            sampleComponents = assignDiff(sampleComponents, changed_components);
            showPage(getCurrentTableId());
            closePopupMessage();
            showPopupMessage("Information",
                "Changes saved. Note that calculations will not run automatically. " +
                "Any parameter changes affecting calculation results require a " +
                "<strong>recalculation</strong>" +
                " to take effect.",
                true);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            closePopupMessage();
            showErrorMessage(XMLHttpRequest, textStatus, errorThrown)
        },
    })
}
function autoChartScale() {
    $.ajax({
        url: url_get_auto_scale,
        type: 'POST',
        data: JSON.stringify({
            'figure_id': getCurrentTableId(),
            'cache_key': cache_key,
        }),
        contentType:'application/json',
        success: function(res){
            if (res.status === 'success') {
                $("input[name='xMin']").val(res.xMin);
                $("input[name='xMax']").val(res.xMax);
                $("input[name='yMin']").val(res.yMin);
                $("input[name='yMax']").val(res.yMax);
            } else {
                // pass
            }
        }
    })
}
function showPage(table_id, recalculate=false) {
    // When current table is isochron table and unsaved changes were detected, a confirm will display
    if (isochron_marks_changed) {
        if (confirm("Save changes to isochron table?")) {
            clickSaveTable();
        } else {isochron_marks_changed = false}
    }
    let tables = document.getElementsByName('table_name')
    const backup = JSON.parse(JSON.stringify(sampleComponents));
    let comp = sampleComponents[table_id];
    for (let i=0; i<tables.length;i++){
        tables[i].classList.remove('active')
    }
    document.getElementById(table_id).classList.add('active');
    setConsoleText(document.getElementById(table_id).innerText);

    switch (table_id) {
        case "0":
            tableContainer.hide();
            tableBtnDiv.show();
            sampleInfoContainer.show();
            figureContainer.hide();
            figure3DContainer.hide();
            figureRightContainer.hide();
            figureBtnDiv.hide();
            thermoPageContainer.hide();
            // update sample information
            $('#exp_name_title').text(sampleComponents['0'].experiment.name);
            $('#inputExpName').val(sampleComponents['0'].experiment.name);
            $('#inputExpType').val(sampleComponents['0'].experiment.type);
            $('#inputSmpName').val(sampleComponents['0'].sample.name);
            $('#inputSmpType').val(sampleComponents['0'].sample.type);
            $('#inputMaterial').val(sampleComponents['0'].sample.material);
            $('#inputLocation').val(sampleComponents['0'].sample.location);
            $('#inputResearcher').val(sampleComponents['0'].researcher.name);
            $('#inputLaboratory').val(sampleComponents['0'].laboratory.name);
            $('#inputLaboratoryMore').val(sampleComponents['0'].laboratory.info);
            $('#inputAnalyst').val(sampleComponents['0'].laboratory.analyst);
            break
        case "1": case "2": case "3": case "4": case "5": case "6": case "7": case "8":
            showTable();
            let header = comp.header.map((col) => String(confidence_level) === '2' ? col.replace("1σ", "2σ") : col.replace("2σ", "1σ"));
            let data = comp.data.map((row) => row.map((col, index) => col = header[index]?.includes("2σ") ? col * 2 : col));
            hot.updateSettings({
                colHeaders: header,
                data: extendData(data),
                columns: comp.coltypes,
            });
            hot.render();
            break
        case "figure_1": case "figure_2": case "figure_3": case "figure_4": case "figure_5": case "figure_6":
            showFigure();
            setRightSideText(confidence_level);
            chart.clear();
            if (table_id==="figure_1") {
                chart = getSpectraEchart(chart, table_id, true, confidence_level, recalculate);
            } else {
                chart = getIsochronEchart(chart, table_id, true, confidence_level);
            }
            chart.resize();
            getChartInterval(chart, comp);
            break
        case "figure_7":
            showFigure();
            setRightSideText(confidence_level);
            figureContainer.hide();
            figure3DContainer.show();
            chart_3D.clear();
            chart_3D = get3DEchart(chart_3D, table_id, true);
            chart_3D.resize();
            break
        case "figure_8":
            showFigure();
            chart.clear();
            chart = getDegasPatternEchart(chart, table_id, false);
            chart.resize();
            comp.xaxis.min = chart._model._componentsMap.get('xAxis')[0].axis.scale._extent[0];
            comp.xaxis.max = chart._model._componentsMap.get('xAxis')[0].axis.scale._extent[1];
            comp.yaxis.min = chart._model._componentsMap.get('yAxis')[0].axis.scale._extent[0];
            comp.yaxis.max = chart._model._componentsMap.get('yAxis')[0].axis.scale._extent[1];
            comp.xaxis.split_number = chart._model._componentsMap.get('xAxis')[0].axis.getTicksCoords().length - 1;
            comp.yaxis.split_number = chart._model._componentsMap.get('yAxis')[0].axis.getTicksCoords().length - 1;
            comp.xaxis.interval = 5;  // category axis don't have interval attribute
            comp.yaxis.interval = chart._model._componentsMap.get('yAxis')[0].axis.scale.getInterval();
            break
        case "figure_9":
            showFigure();
            chart.clear();
            chart = getAgeDistributionEchart(chart, table_id, false);
            chart.resize();
            getChartInterval(chart, comp);
            break
        case "figure_10":
            showThemoPage();
            break
        default:
            break
    }
    updateStyles(backup);
    clickEditFigureStyle(false);
}
function showTable() {
    tableContainer.show();
    tableBtnDiv.show();
    sampleInfoContainer.hide();
    figureContainer.hide();
    figure3DContainer.hide();
    figureRightContainer.hide();
    figureBtnDiv.hide();
    thermoPageContainer.hide();
}
function showFigure() {
    tableContainer.hide();
    tableBtnDiv.hide();
    sampleInfoContainer.hide();
    figureContainer.show();
    figure3DContainer.hide();
    figureRightContainer.show();
    figureBtnDiv.show();
    thermoPageContainer.hide();
}
function showThemoPage() {
    tableContainer.hide();
    tableBtnDiv.hide();
    sampleInfoContainer.hide();
    figureContainer.hide();
    figure3DContainer.hide();
    figureRightContainer.hide();
    figureBtnDiv.hide();
    thermoPageContainer.show();

}
function showUploadPictureBtn() {
    let btn = $('#upload_picture_btn');
    btn.is(":hidden") ? btn.show() : btn.hide();
}
function setConsoleText(text) {
    exampleConsole.innerText = `${getTime()} ${text}`;
    document.getElementById('page-title').innerText = sampleComponents['0'].experiment.name;
}
function setRightSideText(sigma=1) {
    let figure = getCurrentTableId();
    let sample_type = sampleComponents[0].sample?.type;
    let age_unit = sample_type === "Unknown" ? sampleComponents[0].preference?.age_unit : "";
    let flag = sample_type === "Unknown" ? 'Age' : sample_type === "Standard" ? 'J' : sample_type === "Air" ? 'MDF' : '';
    let place = sample_type === "Unknown" ? 2 : 4;
    let text_list = [];
    if (figure === 'figure_7') {
        let iso_res = sampleComponents[0].results.isochron['figure_7'];
        text_list = [
            `z = ${iso_res[0]['m1'].toFixed(place)} x ${iso_res[0]['m2'] > 0?'+':'-'} 
            ${Math.abs(iso_res[0]['m2']).toFixed(place)} y ${iso_res[0]['k'] > 0?'+':'-'} 
            ${Math.abs(iso_res[0]['k']).toFixed(place)}`,
            `t = ${iso_res[0]['age'].toFixed(place)} ± ${(iso_res[0]['s1'] * sigma).toFixed(place)} | ${(iso_res[0]['s2'] * sigma).toFixed(place)} | ${(iso_res[0]['s3'] * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
            `MSWD = ${iso_res[0]['MSWD'].toFixed(place)}, r2 = ${iso_res[0]['R2'].toFixed(place)}, Di = ${iso_res[0]['iter']}, 
            χ2 = ${iso_res[0]['Chisq'].toFixed(place)}, p = ${iso_res[0]['Pvalue'].toFixed(place)}, avg. error = ${iso_res[0]['rs'].toFixed(place)}%`,
            `<sup>40</sup>Ar/<sup>36</sup>Ar = ${iso_res[0]['initial'].toFixed(place)} ± ${(iso_res[0]['sinitial'] * sigma).toFixed(place)} (${sigma}σ)`,
            "", "", "", "", "", "",

            `z = ${iso_res[1]['m1'].toFixed(place)} x ${iso_res[1]['m2'] > 0?'+':'-'} 
            ${Math.abs(iso_res[1]['m2']).toFixed(place)} y ${iso_res[1]['k'] > 0?'+':'-'} 
            ${Math.abs(iso_res[1]['k']).toFixed(place)}`,
            `t = ${iso_res[1]['age'].toFixed(place)} ± ${(iso_res[1]['s1'] * sigma).toFixed(place)} | ${(iso_res[1]['s2'] * sigma).toFixed(place)} | ${(iso_res[1]['s3'] * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
            `MSWD = ${iso_res[1]['MSWD'].toFixed(place)}, r2 = ${iso_res[1]['R2'].toFixed(place)}, Di = ${iso_res[1]['iter']}, 
            χ2 = ${iso_res[1]['Chisq'].toFixed(place)}, p = ${iso_res[1]['Pvalue'].toFixed(place)}, avg. error = ${iso_res[1]['rs'].toFixed(place)}%`,
            `<sup>40</sup>Ar/<sup>36</sup>Ar = ${iso_res[1]['initial'].toFixed(place)} ± ${(iso_res[1]['sinitial'] * sigma).toFixed(place)} (${sigma}σ)`,
            "",

            `Unselected`, `t = ${iso_res[2]['age'].toFixed(place)} ± ${(iso_res[2]['s1'] * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
            `<sup>40</sup>Ar/<sup>36</sup>Ar = ${iso_res[2]['initial'].toFixed(place)} ± ${(iso_res[2]['sinitial'] * sigma).toFixed(place)} (${sigma}σ)`,
            "",
        ]
    }
    if (['figure_1', 'figure_2', 'figure_3', 'figure_4', 'figure_5', 'figure_6'].includes(figure)) {
        let nor_res_set1 = sampleComponents[0].results.isochron.figure_2[0];
        let nor_res_set2 = sampleComponents[0].results.isochron.figure_2[1];
        let inv_res_set1 = sampleComponents[0].results.isochron.figure_3[0];
        let inv_res_set2 = sampleComponents[0].results.isochron.figure_3[1];
        let plateau_set1 = sampleComponents[0].results.age_plateau[0];
        let plateau_set2 = sampleComponents[0].results.age_plateau[1];
        let age_spectra_set1 = sampleComponents[0].results.age_spectra[0];
        let age_spectra_set2 = sampleComponents[0].results.age_spectra[1];
        let total_age = sampleComponents[0].results.age_spectra.TGA;
        let line_coeffs = sampleComponents[0].results.isochron[figure];
        let line1, line2;
        if (figure !== 'figure_1') {
            line1 = `y = ${line_coeffs[0].k.toFixed(4)} + ${line_coeffs[0].m1.toFixed(4)}x`;
            line2 = `y = ${line_coeffs[1].k.toFixed(4)} + ${line_coeffs[1].m1.toFixed(4)}x`;
        } else {
            line1 = "...";
            line2 = "...";
        }
        text_list = [
            `Normal Isochron ${flag} (NI${flag.slice(0,1)})`, `${nor_res_set1.age.toFixed(place)} ± ${(nor_res_set1.s2 * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
            `Inverse Isochron ${flag} (II${flag.slice(0,1)})`, `${inv_res_set1.age.toFixed(place)} ± ${(inv_res_set1.s2 * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
            `Weighted Mean ${flag} (WM${flag.slice(0,1)})`, `${age_spectra_set1.age.toFixed(place)} ± ${(age_spectra_set1.s1 * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
            `Initial Ratio Corrected WM${flag.slice(0,1)}`, `${plateau_set1.age.toFixed(place)} ± ${(plateau_set1.s2 * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
            `Regression Line`, line1,

            `Normal Isochron ${flag} (NI${flag.slice(0,1)})`, `${nor_res_set2.age.toFixed(place)} ± ${(nor_res_set2.s2 * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
            `Inverse Isochron ${flag} (II${flag.slice(0,1)})`, `${inv_res_set2.age.toFixed(place)} ± ${(inv_res_set2.s2 * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
            `Weighted Mean ${flag} (WM${flag.slice(0,1)})`, `${age_spectra_set2.age.toFixed(place)} ± ${(age_spectra_set2.s1 * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
            `Initial Ratio Corrected WM${flag.slice(0,1)}`, `${plateau_set2.age.toFixed(place)} ± ${(plateau_set2.s2 * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
            `Regression Line`, line2,

            `Total ${flag}`, `${total_age.age.toFixed(place)} ± ${(total_age.s2 * sigma).toFixed(place)} ${age_unit} (${sigma}σ)`,
        ];
    }

    let text_containers = document.getElementsByClassName('right-info');
    for (let i=0;i<text_containers.length;i++){
        text_containers[i].innerHTML = text_list[i] === undefined?" ":text_list[i]
    }
}

// Sample instance functions
function assignDiff(target, diff) {
    console.log('=========== UPDATE SAMPLE COMPONENTS =============')
    console.log(diff)
    console.log('================== THE EDN =======================')
    function _assign(a, b) {
        Object.keys(b).map((key)=>{
            if (Object.keys(a).includes(key)) {
                a[key] = typeof a[key] === 'object' ?
                    a[key] instanceof Array || a[key] === null ? b[key]:
                        _assign(a[key], b[key]):b[key];
            } else {a[key] = b[key]}
        })
        return a;
    }
    _assign(target, diff);
    confidence_level = sampleComponents['0'].preference?.confidence_level;
    filePathSpan.innerText = `v=${sampleComponents['0'].arr_version}`;
    return target;
}
function sendDiff(diff) {
    $.ajax({
        url: url_update_components_diff,
        type: 'POST',
        async : true,
        data: JSON.stringify({
            'diff': diff,
            'cache_key': cache_key,
        }),
        contentType:'application/json',
        success: function(res){
            assignDiff(sampleComponents, diff);
        }
    });
}
function findDiff(backup, current) {
    const diff = {};

    if (!isPlainObject(current)) {
        return diff;
    }

    for (const key in current) {
        if (current.hasOwnProperty(key)) {
            if (!backup.hasOwnProperty(key)) {
                diff[key] = current[key];
            } else if (isPlainObject(current[key])) {
                const nestedDiff = findDiff(backup[key], current[key]);
                if (Object.keys(nestedDiff).length > 0) {
                    diff[key] = nestedDiff;
                }
            } else if (JSON.stringify(backup[key]) !== JSON.stringify(current[key])) {
                diff[key] = current[key];
            }
        }
    }

    return diff;
}
function isPlainObject(obj) {
  return typeof obj === 'object' && obj !== null && !Array.isArray(obj);
}

// plots style setting funtions
function dispatchClickComponents(params, type, flag=null) {
    switch (getCurrentTableId()) {
        case 'figure_9':
            switch (type) {
                case 'bar':
                    $("#histogram-element-name").html(params.seriesName);
                    showSettingDialog('histogram-setting-in-dialog');
                    break
                case 'line':
                    $("#kde-element-name").html(params.seriesName);
                    showSettingDialog('kde-setting-in-dialog');
                    break
                case 'custom':
                    $("#agebar-element-name").html(params.seriesName);
                    showSettingDialog('agebar-setting-in-dialog');
                    break
                case 'text':
                    $("#text-element-name").html(flag===null?params.seriesName:flag);
                    showSettingDialog('texts-setting-in-dialog');
                    break
            }
            break
        default:
            switch (type) {
                case 'scatter':
                    $("#scatter-series-name").html(params.seriesName);
                    showSettingDialog('scatters-setting-in-dialog');
                    break
                case 'line':
                    $("#line-series-name").html(params.seriesName);
                    showSettingDialog('lines-setting-in-dialog');
                    break
                case 'text':
                    $("#text-element-name").html(flag===null?params.seriesName:flag);
                    showSettingDialog('texts-setting-in-dialog');
                    break
                case 'custom':
                    $("#custom-series-name").html(params.seriesName)
                    showSettingDialog('custom-setting-in-dialog');
                    break
            }
            break
    }
    initialSettingDialog();
}
function showSettingDialog(id) {
    for (let ele of document.getElementsByClassName('setting-attr-dialog')) {
        ele.id === document.getElementById(id).parentElement.id?ele.show():ele.close();
    }
    $('.setting-dialog:visible').hide();
    $('#'+id).show();
}
function closeSettingDialog() {
    for (let ele of document.getElementsByClassName('setting-attr-dialog')) {
        ele.close();
    }
}
function clickEditFigureStyle(clicked=true) {
    let dialogs = document.getElementsByClassName('setting-attr-dialog');
    let dialog = null;
    let hasDialogOpened = false;
    let show_dialog = (id) => {
        dialog = document.getElementById(id);
        for (let item of dialogs) {
            item.open?hasDialogOpened=true:null;
            item.id === dialog.id?null:item.close();
        }
        if (clicked) {dialog.open?dialog.close():dialog.show();}
        else {hasDialogOpened?dialog.show():dialog.close();}
    }
    switch (getCurrentTableId()) {
        case 'figure_7':
            show_dialog('3DfigurePropertiesDialog');
            dialog.open?$('#3Daxis-setting-in-dialog').show():null;
            break
        case 'figure_8':
            show_dialog('degasPatternPropertiesDialog');
            dialog.open?$.each($('#degasPatternPropertiesDialog :checkbox'), (index, item) => {
                try {
                    item.setAttribute('checked', sampleComponents['figure_8'].info[index]);
                } catch (e) {
                    // pass
                }
            }):null;
            break
        case 'figure_9':
            show_dialog('ageDistributionPropertiesDialog');
            dialog.open?showSettingDialog('figure-9-axis-setting'):null;
            break
        default:
            show_dialog('figurePropertiesDialog');
            dialog.open?showSettingDialog('axis-setting-in-dialog'):null;
            break
    }
    initialSettingDialog();
}
function initialSettingDialog(table_id=null) {
    try {
        let figure = table_id === null?sampleComponents[getCurrentTableId()]:sampleComponents[table_id];
        let option = chart.getOption();
        let series_name, series;
        let get_series = (index, name) => (option['series'][index]['name'] === name ? option['series'][index] : get_series(index+1, name) );

        if (!$('#axis-setting-in-dialog').is(':hidden')){
            $("#axis-setting-in-dialog :input[name='xMin']").val(option.xAxis[0].min);
            $("#axis-setting-in-dialog :input[name='xMax']").val(option.xAxis[0].max);
            $("#axis-setting-in-dialog :input[name='yMin']").val(option.yAxis[0].min);
            $("#axis-setting-in-dialog :input[name='yMax']").val(option.yAxis[0].max);
            $("#axis-setting-in-dialog :input[name='ticksInside']").prop('checked', option.xAxis[0].axisTick.inside);
            // $("#axis-setting-in-dialog :input[name='ticksInside']").prop('checked', option.yAxis[0].axisTick.inside);
            $("#axis-setting-in-dialog :input[name='showXSplitLine']").prop('checked', option.xAxis[0].splitLine.show);
            $("#axis-setting-in-dialog :input[name='showYSplitLine']").prop('checked', option.yAxis[0].splitLine.show);
            $("#axis-setting-in-dialog :input[name='showText1']").prop('checked', figure.text1.show);
            $("#axis-setting-in-dialog :input[name='showText2']").prop('checked', figure.text2.show);
            $("#axis-setting-in-dialog :input[name='showTitle']").prop('checked', option.title.show);
            $("#axis-setting-in-dialog :input[name='showLabel']").prop('checked', option.series[0].label.show);
        }
        if (!$('#figure-9-axis-setting').is(':hidden')){
            $("#figure-9-axis-setting :input[name='xMin']").val(option.xAxis[0].min);
            $("#figure-9-axis-setting :input[name='xMax']").val(option.xAxis[0].max);
            $("#figure-9-axis-setting :input[name='yMin']").val(option.yAxis[0].min);
            $("#figure-9-axis-setting :input[name='yMax']").val(option.yAxis[0].max);
            $("#figure-9-axis-setting :input[name='ticksInside']").prop('checked', option.xAxis[0].axisTick.inside);
            $("#figure-9-axis-setting :input[name='showXSplitLine']").prop('checked', option.xAxis[0].splitLine.show);
            $("#figure-9-axis-setting :input[name='showYSplitLine']").prop('checked', option.yAxis[0].splitLine.show);
            $("#figure-9-axis-setting :input[name='showTitle']").prop('checked', option.title.show);
            $("#figure-9-axis-setting :input[name='showText1']").prop('checked', figure.text1.show);
        }
        if (!$('#scatters-setting-in-dialog').is(':hidden')) {
            series_name = $("#scatter-series-name").html();
            series = get_series(0, series_name === "Series Name" ? "Unselected Points" : series_name);
            $("input[name='fillingColor']").val(series['color'] === 'red' ? '#FF0000' : series['color']);
            $("input[name='borderColor']").val(series['itemStyle']['borderColor']);
            $("input[name='borderWidth']").val(series['itemStyle']['borderWidth']);
            $("input[name='opacity']").val(series['itemStyle']['opacity']);
            $("input[name='symbolSize']").val(series['symbolSize']);
            $("#scatters-setting-in-dialog :input[name='showEllipse']").prop('checked', figure.ellipse.show);
            $("#scatters-setting-in-dialog :input[name='showErrBar']").prop('checked', figure.errline.show);
        }
        if (!$('#lines-setting-in-dialog').is(':hidden')) {
            series_name = $("#line-series-name").html();
            series = get_series(0, series_name);
            $("input[name='lineWidth']").val(series['lineStyle']['width']);
            $("input[name='lineColor']").val(series['color']);
            $("select[name='lineType']").val(series['lineStyle']['type']);
        }
        if (!$('#custom-setting-in-dialog').is(':hidden')) {
            series_name = $("#custom-series-name").html();
            series = get_series(0, series_name);
            $("input[name='errLineColor']").val(series.itemStyle.color);
        }
        if (!$('#texts-setting-in-dialog').is(':hidden')) {
            series_name = $("#text-element-name").html();
            let set = getSetById(table_id===null?getCurrentTableId():table_id, series_name);
            $("#texts-setting-in-dialog select[name='textWeight']").val(set.font_weight);
            $("#texts-setting-in-dialog :input[name='textSize']").val(set.font_size);
            $("#texts-setting-in-dialog :input[name='textFamily']").val(set.font_family);
            $("#texts-setting-in-dialog :input[name='textColor']").val(set.color);
            $("#texts-setting-in-dialog textarea[name='textContent']").val(set.text);
        }
        if (!$('#histogram-setting-in-dialog').is(':hidden')) {
            $("#histogram-setting-in-dialog :input[name='binStart']").val(figure.set1.bin_start);
            $("#histogram-setting-in-dialog select[name='binRule']").val(figure.set1.bin_rule);
            $("#histogram-setting-in-dialog :input[name='binCount']").val(figure.set1.bin_count);
            $("#histogram-setting-in-dialog :input[name='binWidth']").val(figure.set1.bin_width);
            $("#histogram-setting-in-dialog :input[name='fillingColor']").val(figure.set1.color);
            $("#histogram-setting-in-dialog :input[name='borderWidth']").val(figure.set1.border_width);
            $("#histogram-setting-in-dialog select[name='borderType']").val(figure.set1.border_type);
            $("#histogram-setting-in-dialog :input[name='borderColor']").val(figure.set1.border_color);
            $("#histogram-setting-in-dialog :input[name='opacity']").val(figure.set1.opacity);
            $("#histogram-setting-in-dialog :input[name='showLabel']").prop('checked', figure.set1.label.show);
            $("#histogram-setting-in-dialog :input[name='labelColor']").val(figure.set1.label.color);
        }
        if (!$('#kde-setting-in-dialog').is(':hidden')) {
            $("#kde-setting-in-dialog select[name='bandKernel']").val(figure.set2.band_kernel);
            $("#kde-setting-in-dialog select[name='bandAutoWidth']").val(figure.set2.auto_width);
            $("#kde-setting-in-dialog :input[name='bandWidth']").val(figure.set2.band_width);
            $("#kde-setting-in-dialog :input[name='bandPoints']").val(figure.set2.band_points);
            $("#kde-setting-in-dialog :input[name='bandExtend']").prop('checked', figure.set2.band_extend);
            $("#kde-setting-in-dialog :input[name='bandMaximize']").prop('checked', figure.set2.band_maximize);
            $("#kde-setting-in-dialog :input[name='lineWidth']").val(figure.set2.line_width);
            $("#kde-setting-in-dialog :input[name='lineColor']").val(figure.set2.color);
            $("#kde-setting-in-dialog select[name='lineType']").val(figure.set2.line_type);
            $("#kde-setting-in-dialog :input[name='opacity']").val(figure.set2.opacity);
        }
        if (!$('#agebar-setting-in-dialog').is(':hidden')) {
            $("#agebar-setting-in-dialog :input[name='fillingColor']").val(figure.set3.color);
            $("#agebar-setting-in-dialog :input[name='borderColor']").val(figure.set3.border_color);
            $("#agebar-setting-in-dialog :input[name='borderWidth']").val(figure.set3.border_width);
            $("#agebar-setting-in-dialog select[name='borderType']").val(figure.set3.border_type);
            $("#agebar-setting-in-dialog select[name='verticalAlign']").val(figure.set3.vertical_align);
            $("#agebar-setting-in-dialog :input[name='barInterval']").val(figure.set3.bar_interval);
            $("#agebar-setting-in-dialog :input[name='barHeight']").val(figure.set3.bar_height);
            $("#agebar-setting-in-dialog :input[name='opacity']").val(figure.set3.opacity);
        }
    } catch (error) {
        console.log(error);
        closeSettingDialog();
    }
}
function applySettingDialog() {
    let current_component = $('.setting-dialog:visible').attr('id');
    let option = chart.getOption();
    let figure = sampleComponents[getCurrentTableId()];
    let set_name = null;
    const backup = JSON.parse(JSON.stringify(sampleComponents));
    if (current_component==='texts-setting-in-dialog') {
        let text_name = $("#text-element-name").html();
        let text = getSetById(getCurrentTableId(), text_name);
        text.font_weight = $("#texts-setting-in-dialog select[name='textWeight']").val();
        text.font_size = Number($("#texts-setting-in-dialog :input[name='textSize']").val());
        text.font_family = $("#texts-setting-in-dialog :input[name='textFamily']").val();
        text.color = $("#texts-setting-in-dialog :input[name='textColor']").val();
        text.text = $("#texts-setting-in-dialog textarea[name='textContent']").val();
        if (text_name.includes('title')) {
            option = {
                title: {
                    show: text.show, text: text.text, left: 'center', top: '6%',
                    textStyle: {
                        color: text.color, fontWeight: text.font_weight, fontFamily: text.font_family,
                        fontSize: text.font_size
                    },
                    triggerEvent: true, z: 0,
                },
            };
        } else {
            option = {
            series: [
                {
                    id: text_name, name: text_name, type: 'scatter', symbol: 'circle',
                    data: [text.pos], encode: {x: 0, y: 1}, itemStyle: {color: 'none'},
                    label: {
                        show: text.show, position: 'inside', color: text.color, fontSize: text.font_size,
                        fontFamily: text.font_family, fontWeight: text.font_weight, rich: rich_format,
                        formatter: text.text,
                        },
                }
            ],
        };
        }
        chart.setOption(option);
    }
    if (current_component==='axis-setting-in-dialog'){
        figure.xaxis.max = $("#axis-setting-in-dialog :input[name='xMax']").val();
        figure.xaxis.min = $("#axis-setting-in-dialog :input[name='xMin']").val();
        figure.yaxis.max = $("#axis-setting-in-dialog :input[name='yMax']").val();
        figure.yaxis.min = $("#axis-setting-in-dialog :input[name='yMin']").val();
        figure.xaxis.ticks_inside = $("#axis-setting-in-dialog :input[name='ticksInside']").is(':checked');
        figure.yaxis.ticks_inside = $("#axis-setting-in-dialog :input[name='ticksInside']").is(':checked');
        figure.xaxis.show_splitline = $("#axis-setting-in-dialog :input[name='showXSplitLine']").is(':checked');
        figure.yaxis.show_splitline = $("#axis-setting-in-dialog :input[name='showYSplitLine']").is(':checked');
        figure.text1.show = $("#axis-setting-in-dialog :input[name='showText1']").is(':checked');
        figure.text2.show = $("#axis-setting-in-dialog :input[name='showText2']").is(':checked');
        figure.title.show = $("#axis-setting-in-dialog :input[name='showTitle']").is(':checked');
        figure.label.show = $("#axis-setting-in-dialog :input[name='showLabel']").is(':checked');
        showPage(getCurrentTableId());
        // return;  Now changes on xaxis scales can be sent to the backend  2024-02-11
    }
    if (current_component==='figure-9-axis-setting'){
        figure.xaxis.max = $("#figure-9-axis-setting :input[name='xMax']").val();
        figure.xaxis.min = $("#figure-9-axis-setting :input[name='xMin']").val();
        figure.yaxis.max = $("#figure-9-axis-setting :input[name='yMax']").val();
        figure.yaxis.min = $("#figure-9-axis-setting :input[name='yMin']").val();
        figure.xaxis.ticks_inside = $("#figure-9-axis-setting :input[name='ticksInside']").is(':checked');
        figure.yaxis.ticks_inside = $("#figure-9-axis-setting :input[name='ticksInside']").is(':checked');
        figure.xaxis.show_splitline = $("#figure-9-axis-setting :input[name='showXSplitLine']").is(':checked');
        figure.yaxis.show_splitline = $("#figure-9-axis-setting :input[name='showYSplitLine']").is(':checked');
        figure.text1.show = $("#figure-9-axis-setting :input[name='showText1']").is(':checked');
        // let showText2 = $("#figure-9-axis-setting :input[name='showText2']").is(':checked');
        figure.title.show = $("#figure-9-axis-setting :input[name='showTitle']").is(':checked');
        option = {
            title: {show: figure.title.show},
            xAxis: {
                max: figure.xaxis.max, min: figure.xaxis.min,
                axisTick: {inside: figure.xaxis.ticks_inside},
                splitLine: {show: figure.xaxis.show_splitline}
            },
            yAxis: {
                max: figure.yaxis.max, min: figure.yaxis.min,
                axisTick: {inside: figure.yaxis.ticks_inside},
                splitLine: {show: figure.yaxis.show_splitline}
            }
        };
        showPage(getCurrentTableId());
    }
    if (current_component==='histogram-setting-in-dialog'){
        let set1 = getSetById(getCurrentTableId(), 'Histogram');
        set1.bin_start = Number($("#histogram-setting-in-dialog :input[name='binStart']").val());
        set1.bin_rule = $("#histogram-setting-in-dialog select[name='binRule']").val();
        set1.bin_count = Number($("#histogram-setting-in-dialog :input[name='binCount']").val());
        set1.bin_width = Number($("#histogram-setting-in-dialog :input[name='binWidth']").val());
        set1.color = $("#histogram-setting-in-dialog :input[name='fillingColor']").val();
        set1.border_color = $("#histogram-setting-in-dialog :input[name='borderColor']").val();
        set1.border_width = $("#histogram-setting-in-dialog :input[name='borderWidth']").val();
        set1.border_type = $("#histogram-setting-in-dialog select[name='borderType']").val();
        set1.opacity = $("#histogram-setting-in-dialog :input[name='opacity']").val();
        set1.label.show = $("#histogram-setting-in-dialog :input[name='showLabel']").is(':checked');
        set1.label.color =  $("#histogram-setting-in-dialog :input[name='labelColor']").val();
        set1.label.show = $("#histogram-setting-in-dialog :input[name='showLabel']").is(':checked');
    }
    if (current_component==='kde-setting-in-dialog'){
        let set2 = getSetById(getCurrentTableId(), 'KDE');
        set2.band_kernel = $("#kde-setting-in-dialog select[name='bandKernel']").val();
        set2.auto_width = $("#kde-setting-in-dialog select[name='bandAutoWidth']").val();
        set2.band_width = Number($("#kde-setting-in-dialog :input[name='bandWidth']").val());
        set2.band_points = Number($("#kde-setting-in-dialog :input[name='bandPoints']").val());
        set2.band_extend = $("#kde-setting-in-dialog :input[name='bandExtend']").is(':checked');
        set2.band_maximize = $("#kde-setting-in-dialog :input[name='bandMaximize']").is(':checked');
        set2.color = $("#kde-setting-in-dialog :input[name='lineColor']").val();
        set2.line_type = $("#kde-setting-in-dialog select[name='lineType']").val();
        set2.line_width = $("#kde-setting-in-dialog :input[name='lineWidth']").val();
        set2.opacity = $("#kde-setting-in-dialog :input[name='opacity']").val();
    }
    if (current_component==='agebar-setting-in-dialog'){
        let set3 = getSetById(getCurrentTableId(), 'Age Bar');
        set3.color = $("#agebar-setting-in-dialog :input[name='fillingColor']").val();
        set3.border_color = $("#agebar-setting-in-dialog :input[name='borderColor']").val();
        set3.border_width = Number($("#agebar-setting-in-dialog :input[name='borderWidth']").val());
        set3.line_type = $("#agebar-setting-in-dialog select[name='borderType']").val();
        set3.vertical_align = $("#agebar-setting-in-dialog select[name='verticalAlign']").val();
        set3.bar_interval = $("#agebar-setting-in-dialog :input[name='barInterval']").val();
        set3.bar_height = $("#agebar-setting-in-dialog :input[name='barHeight']").val();
        set3.opacity = $("#agebar-setting-in-dialog :input[name='opacity']").val();
    }
    if (current_component==='scatters-setting-in-dialog') {
        set_name = $("#scatter-series-name").html();
        let set = getSetById(getCurrentTableId(), set_name);
        set.color = $("#scatters-setting-in-dialog :input[name='fillingColor']").val();
        set.border_color = $("#scatters-setting-in-dialog :input[name='borderColor']").val();
        set.symbol_size = $("#scatters-setting-in-dialog :input[name='symbolSize']").val();
        set.border_width = $("#scatters-setting-in-dialog :input[name='borderWidth']").val();
        set.opacity = $("#scatters-setting-in-dialog :input[name='opacity']").val();
        figure.ellipse.show = $("#scatters-setting-in-dialog :input[name='showEllipse']").is(':checked');
        figure.errline.show = $("#scatters-setting-in-dialog :input[name='showErrBar']").is(':checked');
        option = {
            series: [
                {
                    name: set_name, color: set.color, symbolSize: set.symbol_size,
                    itemStyle: {borderColor: set.border_color, borderWidth: set.border_width, opacity: set.opacity}
                },
                {
                    name: 'Ellipse', coordinateSystem: figure.ellipse.show?'cartesian2d':'geo',
                },
                {
                    name: 'Error Lines',
                },
            ]
        };
        chart.setOption(option);
    }
    if (current_component==='lines-setting-in-dialog') {
        set_name = $("#line-series-name").html();
        let set = getSetById(getCurrentTableId(), set_name);
        set.line_width = $("input[name='lineWidth']").val();
        set.color = $("input[name='lineColor']").val();
        set.line_type = $("select[name='lineType']").val();
        option = {
            series: [
                {name: set_name, color: set.color, lineStyle: {width: Number(set.line_width), type: set.line_type}}  // 这里如果不用number转一下，直线会超出坐标范围 不知道为什么
            ]
        };
        chart.setOption(option);
    }
    if (current_component==='custom-setting-in-dialog') {
        figure.errline.color = $("input[name='errLineColor']").val();
        option = {
            series: [
                {name: $("#custom-series-name").html(), itemStyle: {color: figure.errline.color}}
            ]
        }
        chart.setOption(option);
    }
    chart.resize();
    getChartInterval(chart, figure);
    // updateStyles(getCurrentTableId(), figure_backup);
    updateStyles(backup);
}
function updateStyles(backup) {
    const diff = (a, b)=>{
        let res = {};
        for (let key in a){
            if (typeof a[key] === 'object' && !Array.isArray(a[key]) && a[key] !== null){
                let _ = diff(a[key], b[key]);
                if (JSON.stringify(_) !== JSON.stringify({})){
                    res[key] = _;
                }
            } else {
                if (JSON.stringify(a[key]) !== JSON.stringify(b[key])){
                    res[key] = b[key];
                }
            }}
        return res
    }
    const changed_styles = diff(backup, sampleComponents)
    if (Object.keys(changed_styles).length === 0) {return}
    $.ajax({
        url: url_update_components_diff,
        type: 'POST',
        data: JSON.stringify({
            'diff': changed_styles,
            'cache_key': cache_key,
        }),
        contentType:'application/json',
        success: function(res){
            if (getCurrentTableId() === 'figure_9') {
                sampleComponents = assignDiff(sampleComponents, res);
                chart.clear();
                chart = getAgeDistributionEchart(chart, getCurrentTableId(), false);
                chart.resize();
                initialSettingDialog();
            }
            setConsoleText("Changes have been applied!");
        }
    });
}

// objetcs-echarts-functions
function changeDegasPlot() {
    let plot_isotopes = [];
    $.each($('#degasPatternPropertiesDialog :checkbox'), (index, item) => (plot_isotopes.push(item.checked)));
    sampleComponents['figure_8'].info = plot_isotopes;
    showPage('figure_8');
}
function getIsochronData(arr, index, mark=5) {
    let data = transpose(arr);
    if (data.length === 0) {
        return [];
    } else {
        return index.map(i => data[arr[mark].indexOf(i)]);
    }
}
function adjustSpectraData(arr, sigma=1) {
    return arr.map((row, index) => [row[0], (row[1] - row[2]) / 2 * (sigma - 1) + row[1], (row[2] - row[1]) / 2 * (sigma - 1) + row[2]])
    // return arr;
}
function getAgeBarData(arr) {
    if (arr.length === 2){
        arr.push(new Array(arr[0].length));
    }
    let transposed = transpose(arr);
    transposed.sort((a, b) => (a[0] - b[0]));
    for (let i=0;i<transposed.length;i++){
        transposed[i][2] = (i + 0.5) / transposed.length;
    }
    return transposed
}
function transpose(arr) {
    if (arr.length===0){return arr}
    const row = arr.length;
    const col = arr[0].length;
    let transposedArr = new Array(col).fill().map(() => new Array(row).fill(0));
    for (let i = 0; i < row; i++) {
        for (let j = 0; j < col; j++) {
          transposedArr[j][i] = arr[i][j];
        }
    }
    return transposedArr;
}
function renderErrBarItem(param, api){
    let sigma = confidence_level;
    const set = sampleComponents[getCurrentTableId()].errline;
    const lineWidth = 1;
    let lineWidth_horizontal = 1;
    let lineWidth_vertical = 1;
    const check = (point) => {
        point = [
            point[0]<param.coordSys.x?param.coordSys.x:point[0]>param.coordSys.x+param.coordSys.width?param.coordSys.x+param.coordSys.width:point[0],
            point[1]<param.coordSys.y?param.coordSys.y:point[1]>param.coordSys.y+param.coordSys.height?param.coordSys.y+param.coordSys.height:point[1],
        ]
        return point
    }
    const getLineWidth = (point) => {
        let _ = point[0] === param.coordSys.x || point[0] === param.coordSys.x+param.coordSys.width || point[1] === param.coordSys.y || point[1] === param.coordSys.y+param.coordSys.height
        return _?0:lineWidth
    }
    let point_1 = check(api.coord([api.value(0)-api.value(1) * sigma, api.value(2)]));
    let point_2 = check(api.coord([api.value(0)+api.value(1) * sigma, api.value(2)]));
    let point_3 = check(api.coord([api.value(0), api.value(2)-api.value(3) * sigma]));
    let point_4 = check(api.coord([api.value(0), api.value(2)+api.value(3) * sigma]));

    if (point_1[1] === param.coordSys.y || point_1[1] === param.coordSys.y+param.coordSys.height){
        lineWidth_horizontal = 0;
    }
    if (point_3[0] === param.coordSys.x || point_3[0] === param.coordSys.x+param.coordSys.width){
        lineWidth_vertical = 0;
    }
    return {
        type: 'group',
        children: [
            {
                type: 'line', ignore: !set.show,
                transition: ['shape'],  // x error bar
                shape: {x1: point_1[0], y1: point_1[1], x2: point_2[0], y2: point_2[1]},
                style: api.style({lineWidth: lineWidth_horizontal, stroke: api.visual('color')})
            },
            {
                type: 'line', ignore: !set.show,
                transition: ['shape'],  // y error bar
                shape: {x1: point_3[0], y1: point_3[1], x2: point_4[0], y2: point_4[1]},
                style: api.style({lineWidth: lineWidth_vertical, stroke: api.visual('color')})
            },
            {
                type: 'line', ignore: !set.show,
                transition: ['shape'],  // left arrow
                shape: {x1: point_1[0], y1: point_1[1]-3, x2: point_1[0], y2: point_1[1]+3},
                style: api.style({lineWidth: getLineWidth(point_1), stroke: api.visual('color')})
            },
            {
                type: 'line', ignore: !set.show,
                transition: ['shape'],  // right arrow
                shape: {x1: point_2[0], y1: point_2[1]-3, x2: point_2[0], y2: point_2[1]+3},
                style: api.style({lineWidth: getLineWidth(point_2), stroke: api.visual('color')})
            },
            {
                type: 'line', ignore: !set.show,
                transition: ['shape'],  // bottom arrow
                shape: {x1: point_3[0] - 3, y1: point_3[1], x2: point_3[0] + 3, y2: point_3[1]},
                style: api.style({lineWidth: getLineWidth(point_3), stroke: api.visual('color')})
            },
            {
                type: 'line', ignore: !set.show,
                transition: ['shape'],  // top arrow
                shape: {x1: point_4[0] - 3, y1: point_4[1], x2: point_4[0] + 3, y2: point_4[1]},
                style: api.style({lineWidth: getLineWidth(point_4), stroke: api.visual('color')})
            },
        ],
    }
}
function renderAgeBarItem(param, api){
    // api.value is a array with three items, [age, sage, n]
    const set = sampleComponents[getCurrentTableId()].set3
    const width = 2 * api.value(1);  // Br width
    const height = set.bar_height;  // Bar height, in px
    const interval = set.bar_interval;  // Bar height, in px
    const align = set.vertical_align;  // Bar height, in px
    const base_height = interval>=0?interval:interval/2;
    // const y = (1 - api.value(2)) * (param.coordSys.height) + param.coordSys.y;
    const y = (n) => {
        switch (align) {
            case 'spread':
                return (1 - n) * (param.coordSys.height - interval) + param.coordSys.y;
            case 'bottom':
                return (param.coordSys.height) - (param.dataIndex + 1) * interval - (param.dataIndex + 1) * height + param.coordSys.y;
            default:
                return (1 - n) * (param.coordSys.height - interval) + param.coordSys.y;
        }
    }
    const letftop_point = api.coord([api.value(0)-api.value(1), 0]);
    const rightbottom_point = api.coord([api.value(0)+api.value(1), 0]);
    if (rightbottom_point[0] < (param.coordSys.x + param.coordSys.width) && letftop_point[0] > param.coordSys.x) {
        return {
            type: 'rect', z2: 9,
            shape: {x: letftop_point[0], y: y(api.value(2)), width: rightbottom_point[0]-letftop_point[0], height: height, r: 0},
            // style: api.style({borderWidth: 1}),
            style: api.style(),
        }
    } else {
        return {type: 'rect', ignore: true}
    }
}
function getIsochronEchart(chart, figure_id, animation, sigma=1) {
    let figure = sampleComponents[figure_id];
    let age_unit = sampleComponents[0].preference?.age_unit;
    // console.log(figure.data);
    let res = sampleComponents[0].results.isochron[figure_id];
    let option = {
        title: {
            show: figure.title.show, text: figure.title.text, left: 'center', top: '6%',
            textStyle: {
                color: figure.title.color, fontWeight: figure.title.font_weight, fontFamily: figure.title.font_family,
                fontSize: figure.title.font_size
            },
            triggerEvent: true, z: 0,
        },
        tooltip: {axisPointer: {type: 'none'}, confine: true, trigger: 'axis',
            formatter: (params) => (tooltipText)},
        grid: {show: false, borderWidth: 1, borderColor: '#222', z: 100,
            top: '5%', left: '8%', bottom: '5%', right: '1%'},
        legend: {
            top: 0, data: [
                {name: 'Unselected Points'},
                {name: 'Points Set 1'},
                {name: 'Points Set 2'},
                {name: 'Line for Set 1'},
                {name: 'Line for Set 2'},
                {name: 'Error Lines', icon: "path://M231.24 14.96l0 -14.96 156.22 0 0 29.93 -156.22 0 0 -14.96zm63.15 261.95l0 -261.95 29.93 0 0 261.95 -29.93 0zm-63.15 0l0 -14.96 156.22 0 0 29.93 -156.22 0 0 -14.96z M14.96 224.05l-14.96 0 0 -156.22 29.93 0 0 156.22 -14.96 0zm588.78 -63.15l-588.78 0 0 -29.93 588.78 0 0 29.93zm0 63.15l-14.96 0 0 -156.22 29.93 0 0 156.22 -14.96 0z"},
                {name: 'Text for Set 1', itemStyle: {color: figure.text1.color}, icon: 'path://M344.1 42.65l0 23.6 -16.07 0 0 45.5c0,9.24 0.14,14.61 0.46,16.13 0.31,1.52 1,2.78 2.11,3.79 1.08,0.97 2.4,1.48 3.96,1.48 2.19,0 5.33,-0.94 9.46,-2.85l1.96 23.09c-5.44,2.96 -11.6,4.44 -18.49,4.44 -4.22,0 -8.01,-0.9 -11.4,-2.71 -3.39,-1.8 -5.87,-4.15 -7.44,-7 -1.6,-2.89 -2.68,-6.75 -3.31,-11.65 -0.49,-3.46 -0.74,-10.46 -0.74,-21.04l0 -49.18 -10.77 0 0 -23.6 10.77 0 0 -22.3 23.42 -17.54 0 39.84 16.07 0zm-156.49 112.36l31.97 -57.88 -30.61 -54.48 28.61 0 15.67 30.89 16.64 -30.89 27.47 0 -30.07 53.22 32.8 59.14 -28.58 0 -18.27 -34.82 -18.18 34.82 -27.47 0zm-41.94 -35.5l23.43 4.98c-2.99,10.86 -7.75,19.12 -14.22,24.82 -6.5,5.67 -14.62,8.52 -24.34,8.52 -15.42,0 -26.85,-6.39 -34.23,-19.16 -5.84,-10.25 -8.78,-23.17 -8.78,-38.79 0,-18.62 3.85,-33.23 11.51,-43.77 7.67,-10.57 17.38,-15.84 29.12,-15.84 13.17,0 23.57,5.52 31.21,16.56 7.61,11.04 11.26,27.96 10.91,50.77l-58.65 0c0.17,8.8 2.05,15.66 5.67,20.57 3.59,4.91 8.09,7.36 13.45,7.36 3.68,0 6.75,-1.26 9.23,-3.79 2.51,-2.52 4.39,-6.6 5.67,-12.23zm-109.42 35.5l0 -128.81 -36.25 0 0 -26.2 97.12 0 0 26.2 -36.08 0 0 128.81 -24.8 0zm110.79 -65.6c-0.17,-8.62 -1.91,-15.19 -5.24,-19.67 -3.33,-4.51 -7.38,-6.75 -12.17,-6.75 -5.1,0 -9.32,2.38 -12.65,7.11 -3.33,4.73 -4.96,11.19 -4.9,19.31l34.97 0z'},
                {name: 'Text for Set 2', itemStyle: {color: figure.text2.color}, icon: 'path://M344.1 42.65l0 23.6 -16.07 0 0 45.5c0,9.24 0.14,14.61 0.46,16.13 0.31,1.52 1,2.78 2.11,3.79 1.08,0.97 2.4,1.48 3.96,1.48 2.19,0 5.33,-0.94 9.46,-2.85l1.96 23.09c-5.44,2.96 -11.6,4.44 -18.49,4.44 -4.22,0 -8.01,-0.9 -11.4,-2.71 -3.39,-1.8 -5.87,-4.15 -7.44,-7 -1.6,-2.89 -2.68,-6.75 -3.31,-11.65 -0.49,-3.46 -0.74,-10.46 -0.74,-21.04l0 -49.18 -10.77 0 0 -23.6 10.77 0 0 -22.3 23.42 -17.54 0 39.84 16.07 0zm-156.49 112.36l31.97 -57.88 -30.61 -54.48 28.61 0 15.67 30.89 16.64 -30.89 27.47 0 -30.07 53.22 32.8 59.14 -28.58 0 -18.27 -34.82 -18.18 34.82 -27.47 0zm-41.94 -35.5l23.43 4.98c-2.99,10.86 -7.75,19.12 -14.22,24.82 -6.5,5.67 -14.62,8.52 -24.34,8.52 -15.42,0 -26.85,-6.39 -34.23,-19.16 -5.84,-10.25 -8.78,-23.17 -8.78,-38.79 0,-18.62 3.85,-33.23 11.51,-43.77 7.67,-10.57 17.38,-15.84 29.12,-15.84 13.17,0 23.57,5.52 31.21,16.56 7.61,11.04 11.26,27.96 10.91,50.77l-58.65 0c0.17,8.8 2.05,15.66 5.67,20.57 3.59,4.91 8.09,7.36 13.45,7.36 3.68,0 6.75,-1.26 9.23,-3.79 2.51,-2.52 4.39,-6.6 5.67,-12.23zm-109.42 35.5l0 -128.81 -36.25 0 0 -26.2 97.12 0 0 26.2 -36.08 0 0 128.81 -24.8 0zm110.79 -65.6c-0.17,-8.62 -1.91,-15.19 -5.24,-19.67 -3.33,-4.51 -7.38,-6.75 -12.17,-6.75 -5.1,0 -9.32,2.38 -12.65,7.11 -3.33,4.73 -4.96,11.19 -4.9,19.31l34.97 0z'},
            ]
        },
        xAxis: [
            {
                name: figure.xaxis.title.text, type: 'value', nameLocation: 'middle', nameGap: 25,
                max: figure.xaxis.max, min: figure.xaxis.min,
                splitLine: {show: figure.xaxis.show_splitline},
                axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}},
                axisLabel: {
                    showMaxLabel: false, color: '#222', fontSize: 10, fontFamily: 'Microsoft Sans Serif',
                },
                axisTick: {inside: figure.xaxis.ticks_inside},
                nameTextStyle: {
                        fontSize: 16, fontFamily: 'Microsoft Sans Serif',
                        rich: {
                            sub: {verticalAlign: "bottom",fontSize: 10, fontFamily: 'Microsoft Sans Serif'},
                            sup: {verticalAlign: "top", fontSize: 10, fontFamily: 'Microsoft Sans Serif'}
                        },
                    },
                zlevel: 9,
            },
            {
                splitLine: {show: false}, axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}},
            },
            {
                id: 'xaxis_for_text', type: 'value', show: false, min: 0, max: 100, position: 'bottom',
            },
        ],
        yAxis: [
            {
                name: figure.yaxis.title.text, type: 'value', nameLocation: 'middle', nameGap: 50,
                max: figure.yaxis.max, min: figure.yaxis.min,
                splitLine: {show: figure.yaxis.show_splitline},
                axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}},
                axisLabel: {
                    showMaxLabel: true, color: '#222', fontSize: 10, fontFamily: 'Microsoft Sans Serif',
                    formatter: function (value) {return getScientificCounting(value)},
                },
                axisTick: {inside: figure.yaxis.ticks_inside},
                nameTextStyle: {
                        fontSize: 16, fontFamily: 'Microsoft Sans Serif',
                        rich: {
                            sub: {verticalAlign: "bottom",fontSize: 10, fontFamily: 'Microsoft Sans Serif'},
                            sup: {verticalAlign: "top", fontSize: 10, fontFamily: 'Microsoft Sans Serif'}
                        },
                    },
                zlevel: 9,
            },
            {
                splitLine: {show: false}, axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}},
            },
            {
                id: 'yaxis_for_text', type: 'value', show: false, min: 0, max: 100, position: 'left',
            },
            {
                id: 'special_yaixs', type: 'value',
                splitLine: {show: false}, axisLine: {show: false, onZero: false},
                position: 'left', min: figure.yaxis.min, max: figure.yaxis.max,
                interval: (figure_id === 'figure_2'?298.56:figure_id === 'figure_3'?0.0033:figure.yaxis.max) - figure.yaxis.min,
                axisTick: {show: false, inside: true},
                axisLabel: {
                    formatter : (value, index) => {
                        if (figure_id !== 'figure_2' && figure_id !== 'figure_3') {
                            return "";
                        }
                        return index === 1?"\u21E6Atmospheric argon ratio":"";
                    },
                    show: figure.label.show, inside: true
                },
            },
        ],
        series: [
            {
                name: 'Unselected Points', type: 'scatter', color: figure.set3.color, symbolSize: figure.set3.symbol_size, z: 2, data: getIsochronData(figure.data, figure.set3.data),
                encode: {x: 0, y: 2}, itemStyle: {borderColor: figure.set3.border_color, borderWidth: figure.set3.border_width, opacity: figure.set3.opacity},
                label: {
                    show: figure.label.show, formatter: (params)=>(params.value[5] + 1), position: figure.label.position, distance: figure.label.distance,
                    offset: figure.label.offset, color: figure.label.color},
                },
            {
                name: 'Points Set 1', type: 'scatter', color: figure.set1.color, symbolSize: figure.set1.symbol_size, z: 2, data: getIsochronData(figure.data, figure.set1.data),
                encode: {x: 0, y: 2}, itemStyle: {borderColor: figure.set1.border_color, borderWidth: figure.set1.border_width, opacity: figure.set1.opacity},
                label: {
                    show: figure.label.show, formatter: (params)=>(params.value[5] + 1), position: figure.label.position, distance: figure.label.distance,
                    offset: figure.label.offset, color: figure.label.color},
                },
            {
                name: 'Points Set 2', type: 'scatter', color: figure.set2.color, symbolSize: figure.set2.symbol_size, z: 2, data: getIsochronData(figure.data, figure.set2.data),
                encode: {x: 0, y: 2}, itemStyle: {borderColor: figure.set2.border_color, borderWidth: figure.set2.border_width, opacity: figure.set2.opacity},
                label: {
                    show: figure.label.show, formatter: (params)=>(params.value[5] + 1), position: figure.label.position, distance: figure.label.distance,
                    offset: figure.label.offset, color: figure.label.color},
                },
            {
                name: 'Line for Set 1', type: 'line', color: figure.line1.color, z: 0, data: figure.line1.data,
                showSymbol: false, clip: true, triggerLineEvent: true,
                label: {show: false, formatter: ''}, lineStyle: {width: figure.line1.line_width, type: figure.line1.line_type},
                },
            {
                name: 'Line for Set 2', type: 'line', color: figure.line2.color, z: 0, data: figure.line2.data,
                showSymbol: false, clip: true, triggerLineEvent: true,
                label: {show: false, formatter: ''}, lineStyle: {width: figure.line2.line_width, type: figure.line2.line_type},
                },
            {
                name: 'Error Lines', type: 'custom', data: transpose(figure.data),
                itemStyle: {color: figure.errline.color}, renderItem: renderErrBarItem, label: {show: false, formatter: ''},
                },
            {
                name: 'Ellipse', type: 'lines', data: figure.ellipse.data.map((item, index) => {
                    return {
                        coords: [
                            ...item, item[0]
                        ],
                    };
                }),
                polyline: true, coordinateSystem: figure.ellipse.show?'cartesian2d':'geo', xAxisIndex: 0, yAxisIndex: 0, silent: true,
                lineStyle:
                    {
                        color: figure.ellipse.border_color, curveness: 0.5, width: figure.ellipse.border_width,
                        type: figure.ellipse.border_type,
                    },
                },
            {
                id: 'Text for Set 1', name: 'Text for Set 1', yAxisIndex: 2, xAxisIndex: 2,
                type: 'scatter', symbol: 'circle',
                data: [figure.text1.pos],
                encode: {x: 0, y: 1}, itemStyle: {color: 'none'},
                label: {
                    show: figure.set1.data.length >=3 ? figure.text1.show : false,
                    position: 'inside', color: figure.text1.color,
                    fontSize: figure.text1.font_size, fontFamily: figure.text1.font_family,
                    fontWeight: figure.text1.font_weight, rich: rich_format,
                    // formatter: figure.text1.text,
                    formatter: (params) => {
                        // if (figure.text1.text === "") {
                        //     figure.text1.text = `t = ${res[0]['age'].toFixed(2)} ± ${res[0]['s1'].toFixed(2)} | ${res[0]['s2'].toFixed(2)} | ${res[0]['s3'].toFixed(2)} Ma\n${figure_id === "figure_2" || figure_id === "figure_3" ?"({sup|40}Ar/{sup|36}Ar){sub|0}":"({sup|40}Ar/{sup|38}Ar){sub|Cl}"} = ${res[0]['initial'].toFixed(2)} ± ${res[0]['sinitial'].toFixed(2)}\nMSWD = ${res[0]['MSWD'].toFixed(2)}, R{sup|2} = ${res[0]['R2'].toFixed(4)}\nχ{sup|2} = ${res[0]['Chisq'].toFixed(2)}, p = ${res[0]['Pvalue'].toFixed(2)}\navg error = ${res[0]['rs'].toFixed(4)}%`;
                        //     let diff = {};
                        //     diff[figure_id] = {'text1': {'text': figure.text1.text}};
                        //     sendDiff(diff);
                        // }
                        // return figure.text1.text
                        if (figure.text1.text === "") {
                            figure.text1.text = `t = ${res[0]['age'].toFixed(2)} ± ${(res[0]['s1'] * sigma).toFixed(2)} | ${(res[0]['s2'] * sigma).toFixed(2)} | ${(res[0]['s3'] * sigma).toFixed(2)} ${age_unit} (${sigma}σ)\n${figure_id === "figure_2" || figure_id === "figure_3" ?"({sup|40}Ar/{sup|36}Ar){sub|0}":"({sup|40}Ar/{sup|38}Ar){sub|Cl}"} = ${res[0]['initial'].toFixed(2)} ± ${(res[0]['sinitial'] * sigma).toFixed(2)} (${sigma}σ)\nMSWD = ${res[0]['MSWD'].toFixed(2)}, R{sup|2} = ${res[0]['R2'].toFixed(4)}\nχ{sup|2} = ${res[0]['Chisq'].toFixed(2)}, p = ${res[0]['Pvalue'].toFixed(2)}\navg error = ${res[0]['rs'].toFixed(4)}%`;
                        }
                        return figure.text1.text
                    },
                },
            },
            {
                id: 'Text for Set 2', name: 'Text for Set 2', yAxisIndex: 2, xAxisIndex: 2,
                type: 'scatter', symbol: 'circle',
                data: [figure.text2.pos],
                encode: {x: 0, y: 1}, itemStyle: {color: 'none'},
                label: {
                    show: figure.set2.data.length >=3 ? figure.text2.show : false,
                    position: 'inside', color: figure.text2.color,
                    fontSize: figure.text2.font_size, fontFamily: figure.text2.font_family,
                    fontWeight: figure.text2.font_weight, rich: rich_format,
                    formatter: (params) => {
                        // if (figure.text2.text === "") {
                        //     figure.text2.text = `t = ${res[1]['age'].toFixed(2)} ± ${res[1]['s1'].toFixed(2)} | ${res[1]['s2'].toFixed(2)} | ${res[1]['s3'].toFixed(2)} Ma\n${figure_id === "figure_2" || figure_id === "figure_3" ?"({sup|40}Ar/{sup|36}Ar){sub|0}":"({sup|40}Ar/{sup|38}Ar){sub|Cl}"} = ${res[1]['initial'].toFixed(2)} ± ${res[1]['sinitial'].toFixed(2)}\nMSWD = ${res[1]['MSWD'].toFixed(2)}, R{sup|2} = ${res[1]['R2'].toFixed(4)}\nχ{sup|2} = ${res[1]['Chisq'].toFixed(2)}, p = ${res[1]['Pvalue'].toFixed(2)}\navg error = ${res[1]['rs'].toFixed(4)}%`;
                        //     let diff = {};
                        //     diff[figure_id] = {'text2': {'text': figure.text2.text}};
                        //     sendDiff(diff);
                        // }
                        // return figure.text2.text
                        if (figure.text2.text === "") {
                            figure.text2.text = `t = ${res[1]['age'].toFixed(2)} ± ${(res[1]['s1'] * sigma).toFixed(2)} | ${(res[1]['s2'] * sigma).toFixed(2)} | ${(res[1]['s3'] * sigma).toFixed(2)} ${age_unit} (${sigma}σ)\n${figure_id === "figure_2" || figure_id === "figure_3" ?"({sup|40}Ar/{sup|36}Ar){sub|0}":"({sup|40}Ar/{sup|38}Ar){sub|Cl}"} = ${res[1]['initial'].toFixed(2)} ± ${(res[1]['sinitial'] * sigma).toFixed(2)} (${sigma}σ)\nMSWD = ${res[1]['MSWD'].toFixed(2)}, R{sup|2} = ${res[1]['R2'].toFixed(4)}\nχ{sup|2} = ${res[1]['Chisq'].toFixed(2)}, p = ${res[1]['Pvalue'].toFixed(2)}\navg error = ${res[1]['rs'].toFixed(4)}%`;
                        }
                        return figure.text2.text
                    },
                },
            },
        ],
        animation: animation,
        animationDuration: 500
    };
    chart.setOption(option);
    return chart
}
function get3DEchart(chart, figure_id, animation) {
    let planerPoints = (xmin, xmax, ymin, ymax, zmin, zmax, a, b ,c) => {
        let p = (f1, f2, f3) => {
            if (f1 === undefined) {f1 = (f3 - b * f2 - c) / a}
            if (f2 === undefined) {f2 = (f3 - a * f1 - c) / b}
            if (f3 === undefined) {f3 = a * f1 + b * f2 + c}
            return [Number(f1), Number(f2), Number(f3)]
        }
        let xnum = 200;
        let ynum = 200;
        let znum = 200;
        let res = [];
        for (let i=0;i<=xnum;i++){
            for (let j=0;j<=ynum;j++){
                res = res.concat([p(xmin + (xmax - xmin) / xnum * i, ymin + (ymax - ymin) / ynum * j, undefined)])
            }
        }
        // for (let i=0;i<=xnum;i++){
        //     for (let j=0;j<=znum;j++){
        //         res = res.concat([p(xmin + (xmax - xmin) / xnum * i, undefined, zmin + (zmax - zmin) / znum * j)])
        //     }
        // }
        // let res = [
        //     p(xmin, ymin, undefined), p(xmin, ymax, undefined),
        //     p(xmax, ymin, undefined), p(xmax, ymax, undefined),
        //     p(xmin, undefined, zmin), p(xmin, undefined, zmax),
        //     p(xmax, undefined, zmin), p(xmax, undefined, zmax),
        //     p(undefined, ymin, zmin), p(undefined, ymin, zmax),
        //     p(undefined, ymax, zmin), p(undefined, ymax, zmax),
        // ];
        // console.log(res);
        // xxx = xxx.slice(0, 3)
        // console.log(xxx);
        // let xxx = res.filter(point => point[0] <= xmax && point[0] >= xmin && point[1] <= ymax && point[1] >= ymin && point[2] <= zmax && point[2] >= zmin);
        let xxx = res.map((point, index) => {
            if (point[2] > zmax){
                return [point[0], point[1], '-']
            }
            if (point[2] < zmin){
                return [point[0], point[1], '-']
            }
            // if (point[2] < zmin){
            //     return [
            //         (b * b * point[0] - a * b * point[1] - a * (c - zmin)) / (a * b * b + a * a),
            //         (a * a * point[1] - a * b * point[0] - b * (c - zmin)) / (a * a + b * b),
            //         zmin]
            // }
            return point
        });
        // let minx=100000, maxx=0.00000001, miny=100000, maxy=0.00000001, minz=100000, maxz=0.00000001;
        // $.each(xxx, (index, point) => {
        //     minx = Math.min(point[0], minx);
        //     maxx = Math.max(point[0], maxx);
        //     miny = Math.min(point[1], miny);
        //     maxy = Math.max(point[1], maxy);
        //     minz = Math.min(point[2], minz);
        //     maxz = Math.max(point[2], maxz);
        // })
        // let yyy = res.filter(point => point[0]===minx || point[0]===maxx || point[1]===miny || point[1]===maxy || point[2]===minz || point[2]===maxz)
        return xxx;
    }
    let figure = sampleComponents[figure_id];
    let regres = sampleComponents[0].results.isochron.figure_7;
    let option = {
        title: {
            show: figure.title.show, text: figure.title.text, left: 'center', top: '6%',
            textStyle: {
                color: figure.title.color, fontWeight: figure.title.font_weight, fontFamily: figure.title.font_family,
                fontSize: figure.title.font_size
            },
            triggerEvent: true, z: 0,
        },
        tooltip: {axisPointer: {type: 'none'}, confine: true, trigger: 'axis',
            formatter: (params) => (tooltipText)},
        legend: {top: 0},
        grid3D: {show: true},
        xAxis3D: {
            name: figure.xaxis.title.text, type: 'value', max: figure.xaxis.max, min: figure.xaxis.min,
            nameTextStyle: {
                fontSize: 16, fontFamily: 'Microsoft YaHei',
                rich:{sub: {verticalAlign: "bottom",fontSize: 10}, sup: {verticalAlign: "top",fontSize: 10},}
                },
        },
        yAxis3D: {
            name: figure.yaxis.title.text, type: 'value', max: figure.yaxis.max, min: figure.yaxis.min,
            nameTextStyle: {
                fontSize: 16, fontFamily: 'Microsoft YaHei',
                rich:{sub: {verticalAlign: "bottom",fontSize: 10}, sup: {verticalAlign: "top",fontSize: 10},}
                },
        },
        zAxis3D: {
            name: figure.zaxis.title.text, type: 'value', max: figure.zaxis.max, min: figure.zaxis.min,
            nameTextStyle: {
                fontSize: 16, fontFamily: 'Microsoft YaHei',
                rich:{sub: {verticalAlign: "bottom",fontSize: 10}, sup: {verticalAlign: "top",fontSize: 10},}
                },
        },
        series: [
            {
                name: 'Unselected Points', type: 'scatter3D', color: figure.set3.color,
                symbolSize: figure.set3.symbol_size, z: 2, coordinateSystemstring: 'cartesian3D',
                data: getIsochronData(figure.data, figure.set3.data, 9), encode: {x: 0, y: 2, z: 4},
                itemStyle: {borderColor: figure.set3.border_color, borderWidth: figure.set3.border_width, opacity: figure.set3.opacity},
            },
            {
                name: 'Points Set 1', type: 'scatter3D', color: figure.set1.color, symbolSize: figure.set1.symbol_size, z: 2,
                data: getIsochronData(figure.data, figure.set1.data, 9), encode: {x: 0, y: 2, z: 4},
                itemStyle: {borderColor: figure.set1.border_color, borderWidth: figure.set1.border_width, opacity: figure.set1.opacity},
            },
            {
                name: 'Points Set 2', type: 'scatter3D', color: figure.set2.color, symbolSize: figure.set2.symbol_size, z: 2,
                data: getIsochronData(figure.data, figure.set2.data, 9), encode: {x: 0, y: 2, z: 4},
                itemStyle: {borderColor: figure.set2.border_color, borderWidth: figure.set2.border_width, opacity: figure.set2.opacity},
            },
            {
                name: 'Unselected Surface', type: 'surface', wireframe: {show: false}, itemStyle: {opacity: 1},
                data: planerPoints(
                    figure.xaxis.min, figure.xaxis.max, figure.yaxis.min, figure.yaxis.max,
                    figure.zaxis.min, figure.zaxis.max,
                    regres[2]['m1'], regres[2]['m2'], regres[2]['k'],
                ),
            },
            {
                name: 'Set 1 Surface', type: 'surface', wireframe: {show: false}, itemStyle: {opacity: 1},
                data: planerPoints(
                    figure.xaxis.min, figure.xaxis.max, figure.yaxis.min, figure.yaxis.max,
                    figure.zaxis.min, figure.zaxis.max,
                    regres[0]['m1'], regres[0]['m2'], regres[0]['k'],
                ),
            },
            {
                name: 'Set 2 Surface', type: 'surface', wireframe: {show: false}, itemStyle: {opacity: 1},
                data: planerPoints(
                    figure.xaxis.min, figure.xaxis.max, figure.yaxis.min, figure.yaxis.max,
                    figure.zaxis.min, figure.zaxis.max,
                    regres[1]['m1'], regres[1]['m2'], regres[1]['k'],
                ),
            },
        ],
    }
    chart_3D.setOption(option);
    return chart_3D
}
function getSpectraEchart(chart, figure_id, animation, sigma=1, recalculate=false) {
    let figure = sampleComponents[figure_id];
    let age_unit = sampleComponents[0].preference?.age_unit;
    let res = sampleComponents[0].results.age_plateau
    let option = {
        title: {
            show: figure.title.show, text: figure.title.text, left: 'center', top: '6%',
            textStyle: {
                color: figure.title.color, fontWeight: figure.title.font_weight, fontFamily: figure.title.font_family,
                fontSize: figure.title.font_size
            },
            triggerEvent: true, z: 0,
        },
        tooltip: {axisPointer: {type: 'none'}, confine: true, trigger: 'axis',
            formatter: (params) => (tooltipText)},
        legend: {
            top: 0, data: [
                {name: 'Spectra Line 1'}, {name: 'Spectra Line 2'},
                {name: 'Set1 Line 1'}, {name: 'Set1 Line 2'},
                {name: 'Set2 Line 1'}, {name: 'Set2 Line 2'},
                {name: 'Text for Set 1', itemStyle: {color: figure.text1.color}, icon: 'path://M344.1 42.65l0 23.6 -16.07 0 0 45.5c0,9.24 0.14,14.61 0.46,16.13 0.31,1.52 1,2.78 2.11,3.79 1.08,0.97 2.4,1.48 3.96,1.48 2.19,0 5.33,-0.94 9.46,-2.85l1.96 23.09c-5.44,2.96 -11.6,4.44 -18.49,4.44 -4.22,0 -8.01,-0.9 -11.4,-2.71 -3.39,-1.8 -5.87,-4.15 -7.44,-7 -1.6,-2.89 -2.68,-6.75 -3.31,-11.65 -0.49,-3.46 -0.74,-10.46 -0.74,-21.04l0 -49.18 -10.77 0 0 -23.6 10.77 0 0 -22.3 23.42 -17.54 0 39.84 16.07 0zm-156.49 112.36l31.97 -57.88 -30.61 -54.48 28.61 0 15.67 30.89 16.64 -30.89 27.47 0 -30.07 53.22 32.8 59.14 -28.58 0 -18.27 -34.82 -18.18 34.82 -27.47 0zm-41.94 -35.5l23.43 4.98c-2.99,10.86 -7.75,19.12 -14.22,24.82 -6.5,5.67 -14.62,8.52 -24.34,8.52 -15.42,0 -26.85,-6.39 -34.23,-19.16 -5.84,-10.25 -8.78,-23.17 -8.78,-38.79 0,-18.62 3.85,-33.23 11.51,-43.77 7.67,-10.57 17.38,-15.84 29.12,-15.84 13.17,0 23.57,5.52 31.21,16.56 7.61,11.04 11.26,27.96 10.91,50.77l-58.65 0c0.17,8.8 2.05,15.66 5.67,20.57 3.59,4.91 8.09,7.36 13.45,7.36 3.68,0 6.75,-1.26 9.23,-3.79 2.51,-2.52 4.39,-6.6 5.67,-12.23zm-109.42 35.5l0 -128.81 -36.25 0 0 -26.2 97.12 0 0 26.2 -36.08 0 0 128.81 -24.8 0zm110.79 -65.6c-0.17,-8.62 -1.91,-15.19 -5.24,-19.67 -3.33,-4.51 -7.38,-6.75 -12.17,-6.75 -5.1,0 -9.32,2.38 -12.65,7.11 -3.33,4.73 -4.96,11.19 -4.9,19.31l34.97 0z'},
                {name: 'Text for Set 2', itemStyle: {color: figure.text2.color}, icon: 'path://M344.1 42.65l0 23.6 -16.07 0 0 45.5c0,9.24 0.14,14.61 0.46,16.13 0.31,1.52 1,2.78 2.11,3.79 1.08,0.97 2.4,1.48 3.96,1.48 2.19,0 5.33,-0.94 9.46,-2.85l1.96 23.09c-5.44,2.96 -11.6,4.44 -18.49,4.44 -4.22,0 -8.01,-0.9 -11.4,-2.71 -3.39,-1.8 -5.87,-4.15 -7.44,-7 -1.6,-2.89 -2.68,-6.75 -3.31,-11.65 -0.49,-3.46 -0.74,-10.46 -0.74,-21.04l0 -49.18 -10.77 0 0 -23.6 10.77 0 0 -22.3 23.42 -17.54 0 39.84 16.07 0zm-156.49 112.36l31.97 -57.88 -30.61 -54.48 28.61 0 15.67 30.89 16.64 -30.89 27.47 0 -30.07 53.22 32.8 59.14 -28.58 0 -18.27 -34.82 -18.18 34.82 -27.47 0zm-41.94 -35.5l23.43 4.98c-2.99,10.86 -7.75,19.12 -14.22,24.82 -6.5,5.67 -14.62,8.52 -24.34,8.52 -15.42,0 -26.85,-6.39 -34.23,-19.16 -5.84,-10.25 -8.78,-23.17 -8.78,-38.79 0,-18.62 3.85,-33.23 11.51,-43.77 7.67,-10.57 17.38,-15.84 29.12,-15.84 13.17,0 23.57,5.52 31.21,16.56 7.61,11.04 11.26,27.96 10.91,50.77l-58.65 0c0.17,8.8 2.05,15.66 5.67,20.57 3.59,4.91 8.09,7.36 13.45,7.36 3.68,0 6.75,-1.26 9.23,-3.79 2.51,-2.52 4.39,-6.6 5.67,-12.23zm-109.42 35.5l0 -128.81 -36.25 0 0 -26.2 97.12 0 0 26.2 -36.08 0 0 128.81 -24.8 0zm110.79 -65.6c-0.17,-8.62 -1.91,-15.19 -5.24,-19.67 -3.33,-4.51 -7.38,-6.75 -12.17,-6.75 -5.1,0 -9.32,2.38 -12.65,7.11 -3.33,4.73 -4.96,11.19 -4.9,19.31l34.97 0z'},
            ]
        },
        grid: {
            show: false, borderWidth: 1, borderColor: '#222', z: 5,
            top: '5%', left: '8%', bottom: '5%', right: '1%',
        },
        xAxis: [
            {
                name: figure.xaxis.title.text, type: 'value', nameLocation: 'middle', nameGap: 25,
                max: figure.xaxis.max, min: figure.xaxis.min,
                splitLine: {show: figure.xaxis.show_splitline},
                axisTick: {inside: figure.xaxis.ticks_inside},
                axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}},
                axisLabel: {showMaxLabel: true, color: '#222'},
                nameTextStyle: {
                        fontSize: 16, fontFamily: 'Microsoft YaHei',
                        rich:{sub: {verticalAlign: "bottom",fontSize: 10}, sup: {verticalAlign: "top",fontSize: 10},}
                    },
                zlevel: 9,
            },
            {splitLine: {show: false}, axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}}},
            {id: 'xaxis_for_text', type: 'value', show: false, min: 0, max: 100, position: 'bottom',},
        ],
        yAxis: [
            {
                name: figure.yaxis.title.text, type: 'value', nameLocation: 'middle', nameGap: 50,
                max: figure.yaxis.max, min: figure.yaxis.min,
                splitLine: {show: figure.yaxis.show_splitline},
                axisTick: {inside: figure.xaxis.ticks_inside},
                axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}},
                axisLabel: {
                    showMaxLabel: true, color: '#222', showMinLabel: false,
                    formatter: function (value) {return getScientificCounting(value)},
                },
                nameTextStyle: {
                        fontSize: 16, fontFamily: 'Microsoft YaHei',
                        rich:{sub: {verticalAlign: "bottom",fontSize: 10}, sup: {verticalAlign: "top",fontSize: 10},}
                    },
                zlevel: 9,
            },
            {splitLine: {show: false}, axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}}},
            {id: 'yaxis_for_text', type: 'value', show: false, min: 0, max: 100, position: 'bottom',},
        ],
        series: [
            {name: 'Spectra Line 1', type: 'line', color: figure.line1.color, encode: {x: 0, y: 1},
                // data: figure.data,
                data: adjustSpectraData(figure.data, sigma),
                seriesLayoutBy: 'row', symbolSize: 0, z: 2, triggerLineEvent: true,
                lineStyle: {width: figure.line1.line_width, type: figure.line1.line_type},
                label: {
                    show: figure.label.show, formatter: (params) => (params.dataIndex%2===0?params.dataIndex/2+1:''),
                    position: figure.line1.label.position, distance: figure.line1.label.distance,
                    offset: figure.line1.label.offset, color: figure.line1.label.color},
                },
            {name: 'Spectra Line 2', type: 'line', color: figure.line2.color, encode: {x: 0, y: 2},
                // data: figure.data,
                data: adjustSpectraData(figure.data, sigma),
                seriesLayoutBy: 'row', symbolSize: 0, z: 2, triggerLineEvent: true,
                lineStyle: {width: figure.line2.line_width, type: figure.line2.line_type},
                label: {
                    show: figure.label.show, formatter: (params) => (params.name), position: figure.line2.label.position,
                    distance: figure.line2.label.distance, offset: figure.line2.label.offset, color: figure.line2.label.color},
                },
            {name: 'Set1 Line 1', type: 'line', color: figure.line3.color, encode: {x: 0, y: 1},
                // data: figure.set1.data,
                data: adjustSpectraData(figure.set1.data, sigma),
                seriesLayoutBy: 'row', symbol: 'none', z: 4, triggerLineEvent: true,
                lineStyle: {width: figure.line3.line_width, type: figure.line3.line_type},
                label: {
                    show: figure.line3.label.show, formatter: (params) => (''), position: figure.line3.label.position,
                    distance: figure.line3.label.distance, offset: figure.line3.label.offset, color: figure.line3.label.color},
                },
            {name: 'Set1 Line 2', type: 'line', color: figure.line4.color, encode: {x: 0, y: 2},
                // data: figure.set1.data,
                data: adjustSpectraData(figure.set1.data, sigma),
                seriesLayoutBy: 'row', symbol: 'none', z: 4, triggerLineEvent: true,
                lineStyle: {width: figure.line4.line_width, type: figure.line4.line_type},
                label: {
                    show: figure.line4.label.show, formatter: (params) => (''), position: figure.line4.label.position,
                    distance: figure.line4.label.distance, offset: figure.line4.label.offset, color: figure.line4.label.color},
                },
            {name: 'Set2 Line 1', type: 'line', color: figure.line5.color, encode: {x: 0, y: 1},
                // data: figure.set2.data,
                data: adjustSpectraData(figure.set2.data, sigma),
                seriesLayoutBy: 'row', symbol: 'none', z: 4, triggerLineEvent: true,
                lineStyle: {width: figure.line5.line_width, type: figure.line5.line_type},
                label: {
                    show: figure.line5.label.show, formatter: (params) => (''), position: figure.line5.label.position,
                    distance: figure.line5.label.distance, offset: figure.line5.label.offset, color: figure.line5.label.color},
                },
            {name: 'Set2 Line 2', type: 'line', color: figure.line6.color, encode: {x: 0, y: 2},
                // data: figure.set2.data,
                data: adjustSpectraData(figure.set2.data, sigma),
                seriesLayoutBy: 'row', symbol: 'none', z: 4, triggerLineEvent: true,
                lineStyle: {width: figure.line6.line_width, type: figure.line6.line_type},
                label: {
                    show: figure.line6.label.show, formatter: (params) => (''), position: figure.line6.label.position,
                    distance: figure.line6.label.distance, offset: figure.line6.label.offset, color: figure.line6.label.color},
                },
            {
                name: 'Set4 Line 1', type: 'line', color: figure.line7.color, encode: {x: 0, y: 1},
                // data: figure.set4.data,
                data: adjustSpectraData(figure.set4.data, sigma),
                seriesLayoutBy: 'row', symbol: 'none', z: 4, triggerLineEvent: true,
                lineStyle: {
                    width: 0, // figure.line7.line_width,
                    type: figure.line7.line_type},
                label: {
                    show: figure.line7.label.show, formatter: (params) => (''), position: figure.line7.label.position,
                    distance: figure.line7.label.distance, offset: figure.line7.label.offset, color: figure.line7.label.color},
                },
            {
                name: 'Set4 Line 2', type: 'line', color: figure.line8.color, encode: {x: 0, y: 2},
                // data: figure.set4.data,
                data: adjustSpectraData(figure.set4.data, sigma),
                seriesLayoutBy: 'row', symbol: 'none', z: 4, triggerLineEvent: true,
                lineStyle: {
                    width: 0, // figure.line8.line_width,
                    type: figure.line8.line_type},
                label: {
                    show: figure.line8.label.show, formatter: (params) => (''), position: figure.line8.label.position,
                    distance: figure.line8.label.distance, offset: figure.line8.label.offset, color: figure.line8.label.color},
                },
            {
                name: 'Set5 Line 1', type: 'line', color: figure.line9.color, encode: {x: 0, y: 1},
                // data: figure.set5.data,
                data: adjustSpectraData(figure.set5.data, sigma),
                seriesLayoutBy: 'row', symbol: 'none', z: 4, triggerLineEvent: true,
                lineStyle: {
                    width: 0, // figure.line9.line_width,
                    type: figure.line9.line_type},
                label: {
                    show: figure.line9.label.show, formatter: (params) => (''), position: figure.line9.label.position,
                    distance: figure.line9.label.distance, offset: figure.line9.label.offset, color: figure.line9.label.color},
                },
            {
                name: 'Set5 Line 2', type: 'line', color: figure.line10.color, encode: {x: 0, y: 2},
                // data: figure.set5.data,
                data: adjustSpectraData(figure.set5.data, sigma),
                seriesLayoutBy: 'row', symbol: 'none', z: 4, triggerLineEvent: true,
                lineStyle: {
                    width: 0, // figure.line10.line_width,
                    type: figure.line10.line_type},
                label: {
                    show: figure.line10.label.show, formatter: (params) => (''), position: figure.line10.label.position,
                    distance: figure.line10.label.distance, offset: figure.line10.label.offset, color: figure.line10.label.color},
                },
            {
                id: 'Text for Set 1', name: 'Text for Set 1', yAxisIndex: 2, xAxisIndex: 2,
                type: 'scatter', symbol: 'circle', z: 5,
                data: [figure.text1.pos], encode: {x: 0, y: 1}, itemStyle: {color: 'none'},
                label: {
                    show: sampleComponents['0'].sample.type === "Unknown" ? figure.set1.data.length >= 3 ? figure.text1.show : false : true,
                    position: 'inside', color: figure.text1.color,
                    fontSize: figure.text1.font_size, fontFamily: figure.text1.font_family,
                    fontWeight: figure.text1.font_weight, rich: rich_format,
                    // formatter: figure.text1.text,
                    formatter: (params) => {
                        if (figure.text1.text === "" || recalculate) {
                            if (sampleComponents['0'].sample.type === "Unknown") {
                                figure.text1.text = `t = ${res[0]['age'].toFixed(2)} ± ${(res[0]['s1'] * sigma).toFixed(2)} | ${(res[0]['s2'] * sigma).toFixed(2)} | ${(res[0]['s3'] * sigma).toFixed(2)} ${age_unit} (${sigma}σ)\nWMF = ${res[0]['F'].toFixed(2)} ± ${(res[0]['sF'] * sigma).toFixed(2)} (${sigma}σ)\nMSWD = ${res[0]['MSWD'].toFixed(2)}, ∑{sup|39}Ar = ${(res[0]['Ar39']*100).toFixed(2)}%\nn = ${res[0]['Num']}, χ{sup|2} = ${res[0]['Chisq'].toFixed(2)}, p = ${res[0]['Pvalue'].toFixed(2)}`;
                            }
                            if (sampleComponents['0'].sample.type === "Standard") {
                                figure.text1.text = `WMF = ${res[0]['F'].toFixed(2)} ± ${(res[0]['sF'] * sigma).toFixed(2)} (${sigma}σ)\nWMJ = ${res[0]['age'].toFixed(6)} ± ${(res[0]['s2'] * sigma).toFixed(6)} (${sigma}σ)\nn = ${res[0]['Num']}, MSWD = ${res[0]['MSWD'].toFixed(2)}\nχ{sup|2} = ${res[0]['Chisq'].toFixed(2)}, p = ${res[0]['Pvalue'].toFixed(2)}`;
                            }
                            if (sampleComponents['0'].sample.type === "Air") {
                                figure.text1.text = `WMAR = ${res[0]['F'].toFixed(2)} ± ${(res[0]['sF'] * sigma).toFixed(2)} (${sigma}σ)\nWMMDF = ${res[0]['age'].toFixed(4)} ± ${(res[0]['s2'] * sigma).toFixed(4)} (${sigma}σ)\nn = ${res[0]['Num']}, MSWD = ${res[0]['MSWD'].toFixed(2)}\nχ{sup|2} = ${res[0]['Chisq'].toFixed(2)}, p = ${res[0]['Pvalue'].toFixed(2)}`;
                                // figure.text1.text = "";
                            }
                        }
                        return figure.text1.text;
                    },
                },
            },
            {
                id: 'Text for Set 2', name: 'Text for Set 2', yAxisIndex: 2, xAxisIndex: 2,
                type: 'scatter', symbol: 'circle', z: 5,
                data: [figure.text2.pos], encode: {x: 0, y: 1}, itemStyle: {color: 'none'},
                label: {
                    show: sampleComponents['0'].sample.type === "Unknown" ? figure.set2.data.length >= 3 ? figure.text2.show : false : true,
                    position: 'inside', color: figure.text2.color,
                    fontSize: figure.text2.font_size, fontFamily: figure.text2.font_family,
                    fontWeight: figure.text2.font_weight, rich: rich_format,
                    // formatter: figure.text2.text,
                    formatter: (params) => {
                        if (figure.text2.text === "") {
                            if (sampleComponents['0'].sample.type === "Unknown") {
                                figure.text2.text = `t = ${res[1]['age'].toFixed(2)} ± ${(res[1]['s1'] * sigma).toFixed(2)} | ${(res[1]['s2'] * sigma).toFixed(2)} | ${(res[1]['s3'] * sigma).toFixed(2)} ${age_unit} (${sigma}σ)\nWMF = ${res[1]['F'].toFixed(2)} ± ${(res[1]['sF'] * sigma).toFixed(2)} (${sigma}σ)\nMSWD = ${res[1]['MSWD'].toFixed(2)}, ∑{sup|39}Ar = ${(res[1]['Ar39']*100).toFixed(2)}%\nn = ${res[1]['Num']}, χ{sup|2} = ${res[1]['Chisq'].toFixed(2)}, p = ${res[1]['Pvalue'].toFixed(2)}`;
                            }
                            if (sampleComponents['0'].sample.type === "Standard") {
                                figure.text2.text = `WMF = ${res[1]['F'].toFixed(2)} ± ${(res[1]['sF'] * sigma).toFixed(2)} (${sigma}σ)\nWMJ = ${res[1]['age'].toFixed(6)} ± ${(res[1]['s2'] * sigma).toFixed(6)} (${sigma}σ)\nn = ${res[1]['Num']}, MSWD = ${res[1]['MSWD'].toFixed(2)}\nχ{sup|2} = ${res[1]['Chisq'].toFixed(2)}, p = ${res[1]['Pvalue'].toFixed(2)}`;
                            }
                            if (sampleComponents['0'].sample.type === "Air") {
                                figure.text2.text = `WMAR = ${res[1]['F'].toFixed(2)} ± ${(res[1]['sF'] * sigma).toFixed(2)} (${sigma}σ)\nWMMDF = ${res[1]['age'].toFixed(4)} ± ${(res[1]['s2'] * sigma).toFixed(4)} (${sigma}σ)\nn = ${res[1]['Num']}, MSWD = ${res[1]['MSWD'].toFixed(2)}\nχ{sup|2} = ${res[1]['Chisq'].toFixed(2)}, p = ${res[1]['Pvalue'].toFixed(2)}`;
                            }
                        }
                        return figure.text2.text;
                    },
                },
            },
        ],
        animation: animation,
        animationDuration: 500
    }
    chart.setOption(option);
    return chart;
}
function getDegasPatternEchart(chart, figure_id, animation) {
    let figure = sampleComponents[figure_id];
    chart.setOption({
        title: {
            show: true, text: figure.title.text, left: 'center', top: '6%',
            textStyle: {
                color: figure.title.color, fontWeight: figure.title.font_weight, fontFamily: figure.title.font_family,
                fontSize: figure.title.font_size
            },
            triggerEvent: true, z: 0,
        },
        grid: {show: false, borderWidth: 1, borderColor: '#222', z: 100,
            top: '5%', left: '8%', bottom: '5%', right: '1%'},
        legend: {top: 0},
        xAxis: [
            {
                name: 'Sequence', type: 'category', nameLocation: 'middle', nameGap: 25,
                axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}},
                axisLabel: {showMaxLabel: false, color: '#222'},
                axisTick: {inside: figure.xaxis.ticks_inside},
                nameTextStyle: {
                        fontSize: 16, fontFamily: 'Microsoft Sans Serif',
                        rich: {
                            sub: {verticalAlign: "bottom",fontSize: 10, fontFamily: 'Microsoft Sans Serif'},
                            sup: {verticalAlign: "top", fontSize: 10, fontFamily: 'Microsoft Sans Serif'}
                        },
                    },
            },
            {splitLine: {show: false}, axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}}},
        ],
        yAxis: [
            {
                name: 'Argon Isotopes (%)', type: 'value', nameLocation: 'middle', nameGap: 50,
                axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}},
                axisLabel: {showMaxLabel: true, color: '#222',},
                axisTick: {inside: figure.xaxis.ticks_inside},
                nameTextStyle: {
                        fontSize: 16, fontFamily: 'Microsoft Sans Serif',
                        rich: {
                            sub: {verticalAlign: "bottom",fontSize: 10, fontFamily: 'Microsoft Sans Serif'},
                            sup: {verticalAlign: "top", fontSize: 10, fontFamily: 'Microsoft Sans Serif'}
                        },
                    },
            },
            {splitLine: {show: false}, axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}}},
        ],
        series: figure.data.map((item, index) => {
            let degas_data = figure.info[index]?item:[];
            degas_data = degas_data.map((v, i) => [i + 1, v]);  // set category of xaxis as index from 1
            return {
                name: ['Ar36a', 'Ar37Ca', 'Ar38Cl', 'Ar39K', 'Ar40*', 'Ar36', 'Ar37', 'Ar38', 'Ar39', 'Ar40'][index],
                type: 'line', symbolSize: 6, z: 2, data: degas_data, silent: true,
                lineStyle: {width: 1, type: 'solid'},
                itemStyle: {borderColor: '#222', borderWidth: 2, opacity: 0.8},
            };
        }),
        animation: animation,
        animationDuration: 500
    })
    return chart;
}
function getAgeDistributionEchart(chart, figure_id, animation) {
    // Age distribution plot, KDE vs. PDP
    let figure = sampleComponents[figure_id];
    chart.setOption({
        title: {
            show: figure.title.show, text: figure.title.text, left: 'center', top: '6%',
            textStyle: {
                color: figure.title.color, fontWeight: figure.title.font_weight, fontFamily: figure.title.font_family,
                fontSize: figure.title.font_size
            },
            triggerEvent: true, z: 0,
        },
        grid: {show: false, borderWidth: 1, borderColor: '#222', z: 100,
            top: '5%', left: '8%', bottom: '5%', right: '1%'},
        legend: {
            top: 0, data: [
                {name: 'Age Histogram', itemStyle: {color: figure.set1.color}, icon: 'path://M 37.324299,21.721424 h 3.262378 V 36.67212 h -3.262378 z M 24.005784,9.4330969 h 3.239762 V 36.660812 h -3.239762 z M 10.676947,17.663985 h 3.23779 v 18.995841 h -3.23779 z'},
                {name: 'Age KDE', itemStyle: {color: 'none', borderWidth: 2, borderColor: figure.set2.color}, icon: 'path://M 1.5520654,44.012985 c 0,0 6.2442905,0.450416 7.9538597,-5.673277 C 12.855863,26.340201 14.068504,8.2787213 15.832858,8.2581363 c 1.934649,-0.02257 3.759255,22.0511597 7.050013,30.3454467 2.219128,5.593265 11.354467,8.15283 14.371339,-0.25328 4.941435,-13.768644 10.816686,-9.276938 13.283894,0.439755'},
                {name: 'Age Bar', itemStyle: {color: figure.set3.color}, icon: 'path://M 20.015251,37.758931 v 3.262378 H 5.0645552 v -3.262378 z M 40.854715,24.429108 v 3.262378 H 19.030694 v -3.262378 z M 47.452914,11.099285 v 3.262378 H 32.502218 v -3.262378 z'},
                {name: 'Text for Set 1', itemStyle: {color: figure.text1.color}, icon: 'path://M344.1 42.65l0 23.6 -16.07 0 0 45.5c0,9.24 0.14,14.61 0.46,16.13 0.31,1.52 1,2.78 2.11,3.79 1.08,0.97 2.4,1.48 3.96,1.48 2.19,0 5.33,-0.94 9.46,-2.85l1.96 23.09c-5.44,2.96 -11.6,4.44 -18.49,4.44 -4.22,0 -8.01,-0.9 -11.4,-2.71 -3.39,-1.8 -5.87,-4.15 -7.44,-7 -1.6,-2.89 -2.68,-6.75 -3.31,-11.65 -0.49,-3.46 -0.74,-10.46 -0.74,-21.04l0 -49.18 -10.77 0 0 -23.6 10.77 0 0 -22.3 23.42 -17.54 0 39.84 16.07 0zm-156.49 112.36l31.97 -57.88 -30.61 -54.48 28.61 0 15.67 30.89 16.64 -30.89 27.47 0 -30.07 53.22 32.8 59.14 -28.58 0 -18.27 -34.82 -18.18 34.82 -27.47 0zm-41.94 -35.5l23.43 4.98c-2.99,10.86 -7.75,19.12 -14.22,24.82 -6.5,5.67 -14.62,8.52 -24.34,8.52 -15.42,0 -26.85,-6.39 -34.23,-19.16 -5.84,-10.25 -8.78,-23.17 -8.78,-38.79 0,-18.62 3.85,-33.23 11.51,-43.77 7.67,-10.57 17.38,-15.84 29.12,-15.84 13.17,0 23.57,5.52 31.21,16.56 7.61,11.04 11.26,27.96 10.91,50.77l-58.65 0c0.17,8.8 2.05,15.66 5.67,20.57 3.59,4.91 8.09,7.36 13.45,7.36 3.68,0 6.75,-1.26 9.23,-3.79 2.51,-2.52 4.39,-6.6 5.67,-12.23zm-109.42 35.5l0 -128.81 -36.25 0 0 -26.2 97.12 0 0 26.2 -36.08 0 0 128.81 -24.8 0zm110.79 -65.6c-0.17,-8.62 -1.91,-15.19 -5.24,-19.67 -3.33,-4.51 -7.38,-6.75 -12.17,-6.75 -5.1,0 -9.32,2.38 -12.65,7.11 -3.33,4.73 -4.96,11.19 -4.9,19.31l34.97 0z'},
            ]
        },
        xAxis: [
            {
                name: figure.xaxis.title.text, type: 'value', nameLocation: 'middle', nameGap: 25,
                min: figure.xaxis.min, max: figure.xaxis.max,
                axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}},
                splitLine: {show: figure.xaxis.show_splitline},
                axisLabel: {showMaxLabel: false, color: '#222'},
                axisTick: {inside: figure.xaxis.ticks_inside},
                nameTextStyle: {
                        fontSize: 16, fontFamily: 'Microsoft Sans Serif',
                        rich: {
                            sub: {verticalAlign: "bottom",fontSize: 10, fontFamily: 'Microsoft Sans Serif'},
                            sup: {verticalAlign: "top", fontSize: 10, fontFamily: 'Microsoft Sans Serif'}
                        },
                    },
            },
            {splitLine: {show: false}, axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}}},
            {id: 'xaxis_for_text', type: 'value', show: false, min: 0, max: 100, position: 'bottom',},
        ],
        yAxis: [
            {
                name: figure.yaxis.title.text, type: 'value', nameLocation: 'middle', nameGap: 50,
                min: figure.yaxis.min, max: figure.yaxis.max,
                axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}},
                splitLine: {show: figure.yaxis.show_splitline},
                axisLabel: {showMaxLabel: false, color: '#222'},
                axisTick: {inside: figure.yaxis.ticks_inside},
                nameTextStyle: {
                        fontSize: 16, fontFamily: 'Microsoft Sans Serif',
                        rich: {
                            sub: {verticalAlign: "bottom",fontSize: 10, fontFamily: 'Microsoft Sans Serif'},
                            sup: {verticalAlign: "top", fontSize: 10, fontFamily: 'Microsoft Sans Serif'}
                        },
                    },
            },
            {
                id: 'KDE Yaxis', type: 'value', min: 0, max: function(val) {
                    if (! figure.set2.band_maximize) {return null}
                    else {return val.max * (figure.yaxis.max - figure.yaxis.min) / Math.max(...figure.set1.data[1])}
                },
                splitLine: {show: false}, axisTick: {show: false}, axisLabel: {show: false},
                axisLine: {show: true, onZero: false, lineStyle: {color: '#222', width: 1}},
            },
            {id: 'yaxis_for_text', type: 'value', show: false, min: 0, max: 100, position: 'left',},
        ],
        series: [
            {
                name: 'Age Histogram', data: transpose(figure.set1.data), type: 'bar', barWidth: '100%',
                encode: {x: 0, y: 1}, z: figure.set1.index, yAxisIndex: 0, bargap: figure.set1.bin_gap,
                itemStyle: {
                    color: figure.set1.color, borderColor: figure.set1.border_color, opacity: figure.set1.opacity,
                    borderType: figure.set1.line_type, borderWidth: figure.set1.border_width,
                },
                label: {
                    show: figure.set1.label.show, position: 'top', formatter: function (params) {
                        return params.data[1]===0?'':`${params.data[1]}\n${params.data[2][0]}~${params.data[2][1]}`
                    }, color: figure.set1.label.color, opacity: 1,
                }
            },
            {
                name: 'Age KDE', data: transpose(figure.set2.data), type: 'line', z: figure.set2.index,
                symbolSize: figure.set2.symbol_size, symbol: figure.set2.symbol, yAxisIndex: 1, triggerLineEvent: true,
                lineStyle: {
                    color: figure.set2.color, type: figure.set2.line_type, width: figure.set2.line_width,
                    opacity: figure.set2.opacity,
                }
            },
            {
                name: 'Age Bar', type: 'custom',
                data: getAgeBarData(figure.set3.data.slice(0, 2)),
                itemStyle: {
                    color: figure.set3.color, borderWidth: figure.set3.border_width,
                    borderColor: figure.set3.border_color, borderType: figure.set3.border_type,
                },
                renderItem: renderAgeBarItem, label: {show: figure.set3.label.show, formatter: ''},
                },
            {
                id: 'Text for Set 1', name: 'Text for Set 1', yAxisIndex: 2, xAxisIndex: 2,
                type: 'scatter', symbol: 'circle', data: [figure.text1.pos],
                encode: {x: 0, y: 1}, itemStyle: {color: 'none'},
                label: {
                    show: figure.text1.show, position: 'inside', color: figure.text1.color, fontSize: figure.text1.font_size,
                    fontFamily: figure.text1.font_family, fontWeight: figure.text1.font_weight, rich: rich_format,
                    formatter: figure.text1.text,
                    },
                },
        ],
        animation: animation,
        animationDuration: 500
    })
    return chart
}
function getScientificCounting(value) {
    if (value === 0) {
        return '0';
    }
    if (Math.abs(value) >= 100000 || Math.abs(value) <= 0.00001) {
        if ((value + '').indexOf('e') > 0) {
            return (value + '').replace(/e/, "E");
        } else {
            let res = value.toString();
            let numN1 = 0;
            let numN2 = 1;
            let num1 = 0;
            let num2 = 0;
            let t1 = 1;
            for (let k = 0; k < res.length; k++) {
                if (res[k] === ".")
                    t1 = 0;
                if (t1)
                    num1++;  // 小数点前的位数
                else
                    num2++;  // 小数点后的位数
            }
            // 均转换为科学计数法表示
            if (Math.abs(value) < 1) {
                // 小数点后一位开始计算
                for (let i = 2; i < res.length; i++) {
                    if (res[i] === "0") {
                        numN2++; //记录10的负指数值（默认值从1开始）
                    } else if (res[i] === "."){}
                    else {break;}
                }
                let v = parseFloat(value);
                // 10的numN2次方
                v = v * Math.pow(10, numN2);
                v = v.toFixed(1); //四舍五入 仅保留一位小数位数
                return v.toString() + "e-" + numN2;
            } else if (num1 > 1) {
                numN1 = num1 - 1;
                let v = parseFloat(value);
                v = v / Math.pow(10, numN1);
                if (num2 > 1) {
                    v = v.toFixed(1);
                }
                return v.toString() + "e" + numN1;
            }
        }
    } else {
        return value;
    }
}
function getChartInterval(chart, figure) {
    figure.xaxis.split_number = chart._model._componentsMap.get('xAxis')[0].axis.getTicksCoords().length - 1;
    figure.yaxis.split_number = chart._model._componentsMap.get('yAxis')[0].axis.getTicksCoords().length - 1;
    figure.xaxis.interval = chart._model._componentsMap.get('xAxis')[0].axis.scale.getInterval();
    figure.yaxis.interval = chart._model._componentsMap.get('yAxis')[0].axis.scale.getInterval();
}
function deepMerge(target, source) {
    if (source.constructor === Array) {
        return source;
    }
    for (let key in source) {
        if (key in target && source[key] instanceof Object) {
            target[key] = deepMerge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
    return target;
}
function extendChartFuncs(chart) {
    chart.clearSeries = (resize=true) => {
        chart.setOption({series: []}, {replaceMerge: ['series']})
        if (resize) {
            chart.resize();
        }
    }
    chart.addSeries = (newSeries, resize=true) => {
        let option = chart.getOption();
        let series = option.series;
        series.push(newSeries);
        chart.setOption({series: series})
        if (resize) {
            chart.resize();
        }
    };
    chart.updateSeries = (newSeries, resize=true) => {
        const id = newSeries.id === undefined ? "" : newSeries.id;
        const name = newSeries.name === undefined ? "" : newSeries.name;
        try {
            let series = deepMerge(chart.getSeries(id, name), newSeries);
            chart.setOption({series: series});
            if (resize) {
                chart.resize();
            }
        } catch (e) {
            // console.log(e);
            chart.addSeries(newSeries, resize);
        }
    };
    chart.showLegend = (showLegend=true) => {
        chart.setOption({legend: {show: showLegend}})
        chart.resize();
    };
    chart.getSeries = (id="", name="") => {
        for (let se of chart.getOption().series) {
            if (se.hasOwnProperty("id") || se.hasOwnProperty("name")) {
                if (se.id === id || se.name === name) {
                    return se;
                }
            }
        }
        // throw `Not found, id = ${id}, name = ${name}`;
    }
    chart.getSeriesByMytype = (myType="") => {
        return chart.getOption().series.filter((se, _) => se.hasOwnProperty("myType") && se.myType === myType)
    }
    chart.registerMouseMove = (seriesId, func) => {
        chart.getZr().on('mousemove', function (event) {
            const series = chart.getSeries(seriesId);
            if (series?.onDragged && series?.draggable) {
                const offset = series.dragOffset;
                let pos = chart.convertFromPixel(
                    {xAxisIndex: series.xAxisIndex, yAxisIndex: series.yAxisIndex},
                    [event.event.zrX - offset?.[0], event.event.zrY - offset?.[1]]
                );
                chart.updateSeries({id: seriesId, data: [pos], animation: false}, false);
            }
        });
        chart.getZr().on('mouseup', function (event) {
            // console.log(event.target.type);  tspan, ec-polyline, rect, path
            if (event.target?.type === "tspan") {
                // mouse up after moving, the target is undefined.
                const series = chart.getSeries(seriesId);
                chart.updateSeries({id: seriesId, onDragged: false, animation: false}, false);
            }
        });
    }
    chart.registerMouseClick = (func) => {
        chart.getZr().on('mousedown', function (event) {
            // console.log("getZr().on(mousedown)");
            // console.log(event);
            // pass
        });
        chart.on('mousedown', (params) => {
            const seriesId = params.seriesId;
            const series = chart.getSeries(seriesId);
            if (series?.draggable) {
                // If draggable like text label, do something
                let pos = chart.convertToPixel({xAxisIndex: series.xAxisIndex, yAxisIndex: series.yAxisIndex}, series.data[0]);
                let offsetX = params.event.offsetX - pos?.[0];
                let offsetY = params.event.offsetY - pos?.[1];
                chart.updateSeries({id: seriesId, onDragged: true, dragOffset: [offsetX, offsetY]}, false);
            } else if (series?.checkable) {
                // else, like a scatter, do something
                func(params);
            }
        });
    }

    chart.getPlotData = () => {
        let data = {};
        let com = chart._model._componentsMap;
        data.name = com.get('title')[0].option.text;
        data.xAxis = com.get('xAxis').map((v, i) => {
            return {
                extent: v.axis.scale._extent, interval: v.axis.scale.getTicks().map(_v => _v.value),
                title: v.option.name, name_location: v.option.nameLocation,
            }
        });
        data.yAxis = com.get('yAxis').map((v, i) => {
            return {
                extent: v.axis.scale._extent, interval: v.axis.scale.getTicks().map(_v => _v.value),
                title: v.option.name, name_location: v.option.nameLocation,
            }
        });
        data.series = com.get('series').map((v, i) => {
            return {
                type: v.type, myType: v.myType, name: v.name, id: v.id, color: v.option.color,
                data: v.option.data.map((_v, _i) => [_v[v.option.encode.x], _v[v.option.encode.y]]),
                text: v.option.myText, fill_color: v.option.color
            }
        });

        return data;

    }

}
function splitByConsecutive(arr) {
    return arr.reduce((result, num, i) => {
        if (i === 0 || num !== arr[i - 1] + 1) {
            result.push([]);
            if (result.length > 1) { result[result.length - 1].push(...result[result.length - 2]) }
        }
        result[result.length - 1].push(num);
        return result;
    }, []);
}
function handsontableRemoveRow(key, options) {
    const rows = [];
    const arr = splitByConsecutive(rows_to_delete);
    options.forEach(item => {
        for (let i = Math.min(item.start.row, item.end.row); i <= Math.max(item.start.row, item.end.row); i++) {
            rows.push(i);
            let flag = false;
            for (let j = arr.length - 1; j >= 0; j--) {
                if (i > Math.max(...arr[j]) - arr[j].length) { rows_to_delete.push(i + arr[j].length); flag = true; break; }
            }
            if (!flag) { rows_to_delete.push(i); }

        }
    });

    rows_to_delete.sort((a, b) => a - b);
    console.log(`The following rows will be deleted: ${rows_to_delete}`);
    let table = sampleComponents[getCurrentTableId()];
    let data = hot.getSourceData().filter((v, i) => ! rows.includes(i));
    hot.updateSettings({
        colHeaders: table.header,
        data: extendData(data),
        columns: table.coltypes
    });
    hot.render();
}
function exportChart(data, download=true) {
    let href = "";
    $.ajax({
        url: url_thermo_export_chart,
        type: 'POST',
        async: false,
        data: JSON.stringify({
            'data': data,
            'settings': getParamsByObjectName('export-pdf'),
        }),
        contentType:'application/json',
        success: function(res){
            if (download) {
                document.getElementById("export_path_link").href = res.href;
                document.getElementById("export_path_link").click();
                document.getElementById("export_path_link").href = '';
            }
            href = res.href;
        }
    });
    return href;
}
function sendWebSocket(flag, postData, onopen, onprogress, onclose, onerror, onfinish) {
    // 1. 调用HTTP接口启动任务
    fetch(`/calc/ws/${flag}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Django CSRF防护
        },
        body: postData
    })
    .then(response => response.json())
    .then(data => {
        if (data.code === 200) {
            const taskId = data.task_id;
            // 2. 建立WebSocket连接
            connectWebSocket(taskId, onopen, onprogress, onclose, onerror, onfinish);
        } else {
            onerror(data.error);
        }
    })
    .catch(error => {
        onerror(error);
    });
}
// 建立WebSocket连接
function connectWebSocket(taskId, onopen, onprogress, onclose, onerror, onfinish) {

    let webSocket = null;
    // 构建WebSocket URL（注意替换为你的域名/端口）
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/progress/${taskId}/`;

    // 创建WebSocket实例
    webSocket = new WebSocket(wsUrl);

    // 连接成功回调
    webSocket.onopen = function(event) { onopen(event); };

    // 接收后端推送的消息（进度）
    webSocket.onmessage = function(event) {
        // const data = JSON.parse(event.data);
        const data = myParse(event.data);
        if (data.error) {
            // 处理错误
            onerror(data);
            if (data.close) {
                onclose(event);
                webSocket.close();
            }
        } else {
            // 更新进度展示
            onprogress(data);
            // 任务完成
            if (data.finished) {
                onfinish(data);
                webSocket.close();
            }
        }
    };

    // 连接关闭回调
    webSocket.onclose = function(event) { onclose(event); };

    // 连接错误回调
    webSocket.onerror = function(error) { onerror(error); };
}
// 获取CSRF Cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function Tree2Json(treeNode, order=0, isArray=false) {
    const json = {};
    const array = [];
    const ulNodes = order===0?treeNode.querySelector('ul.x-tree-root-ct'):treeNode.querySelector('ul.x-tree-node-ct');
    const liNodes = ulNodes.querySelectorAll(':scope > li.x-tree-node');
    liNodes.forEach((liNode) => {
        const div = liNode.querySelector('div.x-tree-node-el');
        const span = liNode.querySelector('span.x-tree-node-key');
        const input = span.querySelector('input');
        if (span) {
            const text = span.textContent.trim();
            const key = text.split(':').map(s => s.trim())[0];
            if (input) {
                let value = (val => {
                    if (val.toLowerCase() === "" || val.includes(" ")) {
                        return val;
                    }
                    // if (val.toLowerCase() === 'nan' || ! Number.isNaN(Number(val))) {
                    //     return Number(val)
                    // }  // 用字符串保存内容
                    if (val.toLowerCase() === 'nan') {
                        return Number(val)
                    }
                    return val
                })(input.value);
                if (isArray) {
                    array.push(value);
                } else {
                    json[key] = value;
                }
            } else {
                if (isArray) {
                    let isArray = div.classList.contains('x-tree-node-expanded');
                    array.push(Tree2Json(liNode, order+1, isArray));
                } else {
                    let isArray = div.classList.contains('x-tree-node-expanded');
                    json[key] = Tree2Json(liNode, order+1, isArray);
                }
            }
        }
    });
    return isArray ? array : json;
}
function Json2Tree(key, value, order=0) {

    // 创建一个li节点表示key:value
    const li = document.createElement('li');
    li.classList.add('x-tree-node');

    const div = document.createElement('div');
    div.classList.add('x-tree-node-el', 'x-unselectable', 'active');

    let span = document.createElement('span');
    span.classList.add('x-tree-node-indent');
    span.innerHTML = "";
    for (let i=0; i<order; i++) {
        span.innerHTML = span.innerHTML + '<img src="/static/image/s.gif" class="x-tree-icon" alt="">';
    }

    let img_1 = document.createElement('img');
    img_1.src = "";
    img_1.alt = "";

    let img_2 = document.createElement('img');
    img_2.src = "";
    img_2.alt = "";

    const text = document.createElement('span');
    text.classList.add('x-tree-node-key');
    // 如果value是基本类型（字符串、数字、布尔值等），直接显示key: value
    if (typeof value !== 'object' || value === null) {
        text.innerHTML = `${key} : <input class="x-tree-node-input" type="text" value="${value}">`;
        img_1.classList.add('x-tree-ec-icon', 'x-tree-elbow-end');
        img_2.classList.add('x-tree-node-icon', 'x-tree-node-inline-icon');
        div.appendChild(span);
        div.appendChild(img_1);
        div.appendChild(img_2);
        div.appendChild(text);
        div.classList.add('x-tree-node-leaf');
        li.appendChild(div);
        return li;
    }
    // 如果value是对象或数组，递归生成子节点
    else {
        text.textContent = `${key} :`;
        img_1.classList.add('x-tree-ec-icon', 'x-tree-elbow-end-plus');
        img_1.onclick = function() { iconOnClick(img_1); }
        if (Array.isArray(value)) {
            img_2.classList.add('x-tree-node-icon', 'x-tree-node-inline-icon');
            div.classList.add('x-tree-node-expanded');
        } else {
            img_2.classList.add('x-tree-node-icon', 'x-tree-node-inline-icon');
            div.classList.add('x-tree-node-collapsed');
        }
        div.appendChild(span);
        div.appendChild(img_1);
        div.appendChild(img_2);
        div.appendChild(text);
        li.appendChild(div);

        const ul_2 = document.createElement('ul');
        ul_2.classList.add('x-tree-node-ct', 'x-tree-lines', 'x-tree-node-nested');

        // 递归处理对象或数组的子元素
        for (const childKey in value) {
            if (value.hasOwnProperty(childKey)) {
                const childLi = Json2Tree(childKey, value[childKey], order+1);
                ul_2.appendChild(childLi);
            }
        }

        li.appendChild(ul_2);

        return li;
    }
}
function iconOnClick(ele, expand=false, collapse=false) {
    let treeNode = ele.closest('.x-tree-node');
    let nestedList = treeNode.querySelector('.x-tree-node-ct');
    if (nestedList === undefined || nestedList === null) {
        return;
    }
    if (!nestedList.classList.contains('x-tree-node-active')) {
        if (collapse) { return; }
        ele.classList.remove('x-tree-elbow-end-plus');
        ele.classList.add('x-tree-elbow-end-minus');
        nestedList.classList.add('x-tree-node-active');
        nestedList.classList.remove('x-tree-node-nested');
    } else {
        if (expand) { return; }
        ele.classList.remove('x-tree-elbow-end-minus');
        ele.classList.add('x-tree-elbow-end-plus');
        nestedList.classList.remove('x-tree-node-active');
        nestedList.classList.add('x-tree-node-nested');
    }
}
