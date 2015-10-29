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