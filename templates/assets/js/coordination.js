function update_coordination() {
    $.ajax({
        type: "GET",
        url: url,
        success: function(data) {
            var mission = data["mission"];
            $("#mission_name").text(mission["name"]);
            $("#text").html(mission["text"]);
            var messages = data["messages"];
            $("#messages").html(messages);
            var hints = data["hints"];
            $("#hints").html(hints);
            var wrong_keys = data["wrong_keys"];
            $("#wrong_keys").html(wrong_keys);
            var completed_missions = data["completed_missions"];
            $("#completed_missions").html(completed_missions);
            var hide_form = data["hide_form"];
            if (hide_form) {
                $("#form").empty();
            }
            start_countdown(data["delay"]);
        }
    });
}

function start_countdown(time) {
    var countdown = $('#countdown');
    countdown.countdown('destroy');
    if (time != null) {
        countdown.countdown({
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
