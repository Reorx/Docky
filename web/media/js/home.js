(function ($) {
    var docky = $.sammy(function () {

        /* urls */
        var urls = {
            home: '#!/',
            history: {
                list: [],
                last: null,
            },
            current: function () {
                         return window.location.href;
                     }
        }
        urls.history.log = function (path) {
            urls.history.list[urls.history.list.length] = path;
            urls.history.last = path;
        }
        urls.history.is_last = function (path) {
            if (path == urls.history.last) {
                return true;
            } else {
                return false;
            }
        }
        urls.about =  urls.home + 'about';
        urls.projects =  urls.home + 'projects';
        urls.projects_show =  urls.projects + '/:name';
        urls.projects_resources = urls.projects_show + '/rs';

        /* templates */
        var tmpls = {};
        tmpls.project = '<p>{{description}}</p>'+
                        '<p class="info">{{created_time}}</p>'+
                        '<div class="extra">'+
                          '<h3>Sections</h3>'+
                          '<ul>'+
                              '{{#sections}}'+
                              '<li>{{name}}</li>'+
                              '{{/sections}}'+
                          '</ul>'+
                          '<div class="modal-footer">'+
                              '<div class="form">'+
                                  '<form>'+
                                      '<div><input class="span4" type="text" name="name" placeholder="name"></div>'+
                                      '<div><textarea class="span6" name="description" rows="3" placeholder="description"></textarea></div>'+
                                  '</form>'+
                              '</div>'+
                              '<div class="acts">'+
                                  '<a id="section-create" class="btn">Create</a>'+
                              '</div>'+
                          '</div>'+
                        '</div>';
        tmpls.home_li = '<li class="home">'+
                            '<a href="{{url}}">{{name}}</a>'+
                        '</li>';
        tmpls.projects_li = '<li class="project">'+
                                '<a href="{{url}}">{{name}}</a>'+
                            '</li>';

        /* DOM objects */
        var $o = {
            $: $('body'),
            topbar: {},
            sidebar: {},
            main: {},
        }
        $o.topbar.$ = $o.$.find('#topbar');
        $o.topbar.h = $o.topbar.$.find('h4');
        $o.topbar.$fn = {}
        $o.topbar.$fn.set_h = function (text) {
            $o.topbar.h.animate({
                opacity: 0,
            }, 300, function () {
                $(this).html(text).animate({
                    opacity: 1,
                }, 500);
            });
        }
        $o.sidebar.$ = $o.$.find('#sidebar');
        $o.sidebar.index = $o.sidebar.$.find('ul.index');
        $o.sidebar.acts = $o.sidebar.$.find('.acts');
        $o.sidebar.$fn = {};
        $o.sidebar.$fn.index = function (style, json) {
            // styles: home, projects, sections
            $o.sidebar.index.empty();
            switch (style) {
                case 'home':
                    $.each(json, function (i, j) {
                        $.mustache(tmpls.home_li, j).appendTo($o.sidebar.index);
                    });
                    break
                case 'projects':
                    $.each(json, function (i, j) {
                        j.url = urls.projects + '/' + j.name;
                        $.mustache(tmpls.projects_li, j).appendTo($o.sidebar.index);
                    });
                    break
                case 'sections':
                    break
            }
        }
        $o.sidebar.$fn.acts = function (sign) {
            $o.sidebar.acts.empty();
            switch (sign) {
                case 'projects':
                    var btn = $('<a />').addClass('btn primary')
                                        .attr('id', 'project-create')
                                        .html('Create');
                    $o.sidebar.acts.append(btn)
                    break
                case 'project':
                    var $t = $o.sidebar.acts;
                    var btn = $('<a />').addClass('btn')
                                        .attr('href', urls.current()+'/rs')
                                        .html('Resources').appendTo($t);
                    var btn = $('<a />').addClass('btn info')
                                        .attr('id', 'project-edit')
                                        .html('Edit').appendTo($t);
                    var btn = $('<a />').addClass('btn danger')
                                        .attr('id', 'project-delete')
                                        .html('Delete').appendTo($t)
                    break
                case 'resource':
                    var btn = $('<a />').addClass('btn primary')
                                        .attr('id', 'resource-create')
                                        .html('Create');
                    break
            }
        }
        $o.main.$ = $o.$.find('#main');
        $o.main.h = $o.main.$.find('.page-header h2');
        $o.main.content = $o.main.$.find('.content .row .spanMax');
        $o.main.$fn = {};
        $o.main.$fn.set_h = function (html) {
            $o.main.h.html(html);
        }
        $o.main.$fn.set_content = function (html) {
            $o.main.content.html(html);
        }

        /* functions */
        $fn = {};
        $fn.submit_section = function () {
            var form = $o.main.content.find('form');
            var data = {
                name: form.find('input[name="name"]').val(),
                description: form.find('textarea[name="description"]').val(),
            }
            var p_name = $.url().fsegment(-1);
            $.ajax({
                type: 'POST',
                url: '/projects/name:'+p_name+'/sections',
                data: data,
                success: function (resp) {
                    alert('ye');
                }
                
            });
        }
        $fn.bind_section_create = function () {
            //var $t = $o.btn.section_create;
            var $t = $('#section-create');
            $t.bind('click', function () {
                var formLayer = $o.main.content.find('div.form');
                formLayer.animate({
                    height: '120px',
                }, 500, function () {
                    formLayer.find('form').fadeIn(500);

                    $t.addClass('primary').html('Submit')
                      .unbind().bind('click', function () {
                          $fn.submit_section();
                      });
                });
            });
        }

        /* views */
        // home
        this.get(urls.home, function (context) {
            context.log(context);
            $o.topbar.$fn.set_h('Docky');
            var ul_raw = [
                {name: 'what is docky',
                 url: urls.about},
                {name: 'projects',
                 url: urls.projects},
            ]
            $o.sidebar.$fn.index('home', ul_raw);

        urls.history.log(context.path);
        context.log(urls);
        });

        // projects
        this.get(urls.projects, function (context) {
            $o.topbar.$fn.set_h('Projects');
            $o.sidebar.$fn.acts('projects');

            context.load('/projects')
                   .then(function (json) {
                        $o.sidebar.$fn.index('projects', json);
                        // set signal
                   });
        });

        // projects_show
        this.get(urls.projects_show, function (context) {
            $o.topbar.$fn.set_h('Project: '+context.params.name);
            $o.sidebar.$fn.acts('project');
            context.load('/projects/name:' + context.params.name)
                   .then(function (json) {
                       $o.sidebar.$fn.index('sections', json.sections);
                       $o.main.$fn.set_h(json.name);
                       html = $.mustache(tmpls.project, json);
                       $o.main.$fn.set_content(html);

                       $fn.bind_section_create();
                   });
        });

        // projects_resources
        this.get(urls.projects_resources, function (context) {
            context.load('/projects/name:'+context.params.name+'/rs')
                   .then(function (json) {
                       /* json:
                        * [
                        *    {'name': '',
                        *     'sequence': 1,
                        *     'resources': [
                        *         {...},
                        *     ] },
                        * ]
                        */
                   });
        });

    });

    // lives

    // start app
    $(function () {
        docky.run('#!/');
    });

})(jQuery);

$(function () {
    //$.meow({ message: 'ofck', })
})
