$(function () {
    $(function () {
        $('#id_start').datetimepicker({
            locale: 'ru',
            useCurrent: false,
            stepping: 5,
            sideBySide: true,
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

        $('#id_game_over').datetimepicker({
            locale: 'ru',
            useCurrent: false,
            stepping: 5,
            sideBySide: true,
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
});