function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(';') : [];

    for (const cookie of cookies) {
        const value = cookie.trim();

        if (value.startsWith(name + '=')) {
            return decodeURIComponent(value.slice(name.length + 1));
        }
    }

    return null;
}


function getCsrfToken() {
    const input = document.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    );

    if (input && input.value) {
        return input.value;
    }

    const meta = document.querySelector(
        'meta[name="csrf-token"]'
    );

    if (meta && meta.content && meta.content !== 'NOTPROVIDED') {
        return meta.content;
    }

    return getCookie('csrftoken');
}


function csrfSafeMethod(method) {
    return /^(GET|HEAD|OPTIONS|TRACE)$/i.test(method);
}


function setCsrfHeader(xhr) {
    const token = getCsrfToken();

    if (token) {
        xhr.setRequestHeader('X-CSRFToken', token);
    }
}


$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (
            !csrfSafeMethod(settings.type) &&
            !settings.crossDomain
        ) {
            setCsrfHeader(xhr);
        }
    }
});

