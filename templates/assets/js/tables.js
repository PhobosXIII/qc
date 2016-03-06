function playerFormatter(index, row) {
    var html = [];
    $.each(row, function (key, value) {
        if (key == 5) {
            html.push('<p><b>Взяты:</b> ' + value + '</p>');
        }
    });
    return html.join('');
}

function missionFormatter(index, row) {
    var html = [];
    $.each(row, function (key, value) {
        if (key == 2) {
            html.push('<p><b>Взяли:</b> ' + value + '</p>');
        }
    });
    return html.join('');
}