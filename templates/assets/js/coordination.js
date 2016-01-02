function update_coordination() {
    $.ajax({
        type: "GET",
        url: url,
        success: function(data) {
            $("#messages").empty();
            $("#hints").empty();
            var mission = data["mission"];
            $("#mission_name").text(mission["name"]);
            $("#text").html(mission["text"]);
            var messages = data["messages"];
            $.each(messages, function(key,message) {
                $("#messages").append('<p class="alert alert-info">' + message.text + '</p>');
            });
            var hints = data["hints"];
            $.each(hints, function(key,hint) {
                $("#hints").append(
                        '<div class="col-md-4">' +
                        '<div class="panel panel-primary">' +
                        '<div class="panel-heading">' +
                        '<h4 class="panel-title">' +
                        hint.title +
                        '<span class="pull-right"><span class="fa fa-clock-o fa-lg"></span> ' +
                        hint.delay +
                        '</span></h4></div>' +
                        '<div class="panel-body">' +
                        '<div class="text-base">' +
                        hint.text +
                        '</div></div></div></div>'
                );
            });
            start_countdown(data["delay"]);
        }
    });
}

function start_countdown(time) {
    $('#countdown').countdown('destroy');
    if (time != null) {
        $('#countdown').countdown({
            until: +time, compact: true,
            layout: 'До следующей подсказки осталось: <b>{mnn}{sep}{snn}</b>.' +
            ' Если подсказка не отобразилась, обновите страницу вручную!',
            onExpiry: refresh
        });
    }
}

function refresh() {
    sleep(1500);
    update_coordination()
}

function sleep(duration) {
    var d = new Date().getTime() + duration;
    while(new Date().getTime() <= d ) {}
}
