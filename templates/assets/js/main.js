$(function () {
    $(function () {
        $('#id_start').datetimepicker({
            locale: 'ru',
            useCurrent: false,
            stepping: 5,
            sideBySide: true,
            minDate: moment().subtract(4, 'hours'),
            icons: {
                time: "fa fa-clock-o",
                date: "fa fa-calendar",
                up: "fa fa-chevron-up",
                down: "fa fa-chevron-down",
                previous: "fa fa-chevron-left",
                next: "fa fa-chevron-right",
                today: 'fa fa-bullseye',
                clear: 'fa fa-trash',
                close: 'fa fa-remove'
            }
        });
    });

    $('#confirm').on('show.bs.modal', function(e) {
        $(this).find('.btn-ok').attr('href', $(e.relatedTarget).data('href'));
    });
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});
