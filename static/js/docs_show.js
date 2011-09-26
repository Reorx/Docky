$(function () {

    // 添加参数(parameter)按钮的点击事件
    var parameter_adder = $('#parameter_adder').click(function () {
        var f = $('#parameters_field');
        var param = {};
        f_name = f.find('input[name="parameter_name"]');
        f_required = f.find('input[name="parameter_required"]');
        f_description = f.find('textarea[name="parameter_description"]');
        param.name = f_name.val();
        param.required = f_required.attr('checked')?'true':'false';
        param.description = f_description.val();
        if (param.name && param.description) {
            var tmpl = '<div class="item">' +
                            '<a href="#" class="close">x</a>' +
                            '<div class="info">' +
                                '<div class="name">${name}</div>' +
                                '<div class="required">${required}</div>' +
                            '</div>' +
                            '<div class="description">${description}</div>' +
                       '</div>';
            var box = $('#static_parameters');
            var paramNode = $.tmpl(tmpl, param);
            if (param.required) {
                var label = $('<span />').addClass('label important').html('required');
                paramNode.find('.name').after(label);
            }
            box.append(paramNode);
            //alert(param.name);
            f_name.val('');
            f_required.attr('checked', false);
            f_description.val('');
            // append sth
        }
        return false;
    });

    // 取消参数的按钮点击事件
    var parameter_closer = $('#static_parameters .item').find('a.close').live('click', function () {
        $this = $(this);
        $this.parent().remove();
        return false;
    });

    // 返回样例editor按键事件
    // 每次按下，将输入放入<pre>中并执行prettyPrint
    // 如果按下Tab键，插入四个空格
    var counter0 = 0;
    var code_raws = $('form textarea.code_raw').bind({
        keydown: function (e) {
            var keyCode = e.keyCode || e.which;
            if (keyCode == 9) {
                $(this).val($(this).val() + '    ');
                return false;
            }
        },
        keyup: function (e) {
            counter0 += 1;
            var code_syntaxeds = $('form pre.code_syntaxed');
            code_syntaxeds.html($(this).val());
            /* if (counter0%5 == 0) {
            } */
            prettyPrint();
        },
    });

    // 文档条目提交按钮
    // 首先遍历所有输入控件，获取各值，组合成对象并转化为json字符串进行提交
    var submit_btn = $('#entry_submit').click(function () {
        var form = $('#entry_form');
        var _f = function (k) {
            buf = form.find('[name="'+k+'"]').eq(0);
            if (buf && buf.val()) {
                return buf.val();
            } else {
                return '';
            }
        }
        var d = {};
        d.doc = _f('doc');
        d.resource = _f('resource');
        d.url = _f('url');
        d.method = _f('method');
        d.description = _f('description');
        d.authentication_required = form.find('[name="authentication_required"]').attr('checked')?'true':'false';
        d.parameters = [];
        $('#static_parameters').find('.item').each(function () {
            var p = {};
            p.name = $(this).find('.name').html();
            p.required = $(this).find('.required').html();
            p.description = $(this).find('.description').html();
            d.parameters.push(p);
        });
        d.example = {};
        d.example.request = _f('example_request');
        d.example.response = _f('example_response');
        for (i in d) {
            if (!d[i]) {
                popNoti(i);
                return false
            }
        }

        var ajax = new_ajax('POST');
        ajax.data.data = $.toJSON(d);
        ajax.url = '/entries';
        ajax.send(function (resp) {
            window.location.href = '/docs/' + d.doc;
        });

        return false;
    });

    var entries = $('#entries');

    var entryform = $('#entryform');

    // 左侧栏两个按钮点击事件
    // 转换显示内容
    var tgr_all = $('#tgr_all').click(function () {
        entryform.hide();
        entries.show();
        return false;
    });
    var tgr_add = $('#tgr_add').click(function () {
        entries.hide();
        entryform.show();
        return false;
    });
});
