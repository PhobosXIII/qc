function nlPlayerFormatter(index, row) {
    var html = [];
    $.each(row, function (key, value) {
        if (key == 5) {
            html.push('<p><b>Взяты:</b> ' + value + '</p>');
        }
    });
    return html.join('');
}

function nlMissionFormatter(index, row) {
    var html = [];
    $.each(row, function (key, value) {
        if (key == 2) {
            html.push('<p><b>Взяли:</b> ' + value + '</p>');
        }
    });
    return html.join('');
}

function mlPlayerFormatter(index, row) {
    var html = [];
    $.each(row, function (key, value) {
        if (key == 6) {
            html.push('<p><b>Взяты:</b> ' + value + '</p>');
        }
    });
    return html.join('');
}

function mlMissionFormatter(index, row) {
    var html = [];
    $.each(row, function (key, value) {
        if (key == 2) {
            html.push('<p><b>Взяли:</b> ' + value + '</p>');
        }
    });
    return html.join('');
}