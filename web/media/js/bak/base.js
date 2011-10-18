/* components */
var popNoti = function (s, hold) {
    var noti = $('<span>').html(s).appendTo($('#popNoti'));
    noti.close = function (msg) {
        if (msg) { noti.html(msg); }
        noti.fadeOut(300, function () {
            var gap = $('<span>').addClass('gap');
            noti.after(gap);
            gap.animate({
                height: '0px'
            }, 300, function () {
                gap.remove();
                noti.remove();
            });
        })
    }

    if (hold) {
        noti.fadeIn(300);
        return noti;
    } else {
        noti.fadeIn(300, function () {
            setTimeout(function () {
                noti.close();
            }, 500);
        });
    }
}

var new_ajax = function (method) {
    var ajaxObj = {};
    ajaxObj.method = method;
    ajaxObj.url = '';
    ajaxObj.data = {};
    ajaxObj.send = function (succFn) {
        $.ajax({
            type: ajaxObj.method,
            url: ajaxObj.url,
            /*
            headers: {
                'Cookie': 'global_session_id='
            },
            */
            beforeSend: function(jqXHR) {
                ajaxObj.noti = popNoti('before', true);
            },
            data: ajaxObj.data,
            success: succFn,
            complete: function (jqXHR, msg) {
                //popNoti('ajax: ' + jqXHR.status + ' ' + msg);
                ajaxObj.noti.html(msg).fadeOut();
            }
        });
    };
    return ajaxObj;
}

$(function () {
    $('textarea').elastic();
});
