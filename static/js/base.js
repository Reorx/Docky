var popNoti = function (s) {
    var notiDOM = $('<div>').css({
        'display': 'none',
        'position': 'absolute',
        'height': '30px', 'line-height': '30px',
        'text-align': 'center',
        'top': '20px', 'right': '20px',
    }).append(
        $('<span>').html(s).css({
            'padding': '2px 8px',
            'background': 'red', 'color': '#fff'
        })
    );
    $('body').append(notiDOM);
    notiDOM.fadeIn(1200, function () {
        setTimeout(function () {
            notiDOM.fadeOut(1200, function () {
                notiDOM.remove();
            })
        }, 800);
    });
}

var new_ajax = function () {
    var ajaxObj = {};
    ajaxObj.method = 'POST';
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
            beforeSend: function(jqXHR) {
                var header_cookie_val = 'global_session_id='+api_token;
                jqXHR.setRequestHeader("Cookie", header_cookie_val);
            },
            */
            data: ajaxObj.data,
            success: succFn
        });
    };
    return ajaxObj;
}

$(function () {
    $('#main_tab .tab').each(function () {
        var xfocus = '{{ main_tab }}';
        if (xfocus == $(this).attr('xid')) {
            $(this).addClass('focus');
        }
    });
    /*
    $('h1.mx').mouseover(function () {
        $(this).find('a.hidden').delay(300).css({'display': 'block'});
    }).mouseleave(function () {
        $(this).find('a.hidden').hide(300);
    });
    */
});
