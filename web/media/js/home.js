
(function ($) {
  /*
  var ms = function (tmpl_url, obj) {
    $.get(tmpl_url, function (tmpl) {
      return Mustache.to_html(tmpl, obj);
    });
  }
  */

  var docky = $.sammy(function () {

    this.last = null;

    var $sidebar = $('body .container-fluid > .sidebar');
    var $sidebar_h2 = $sidebar.find('h2');
    var $sidebar_ul = $sidebar.find('ul');

    var set_sidebar_h2 = function (text) {
      /*
      $sidebar_h2.fadeOut(300, function () {
        $this = $(this);
        $this.html(text).fadeIn(300);
      });
      */
      $sidebar_h2.animate({
        //'color': 'transparent',
        opacity: 0,
      }, 150, function () {
        $(this).html(text).animate({
          opacity: 1,
        }, 300);
      });
    }
    var set_sidebar_ul = function (ul) {
      $sidebar_ul.height($sidebar_ul.height());
      $sidebar_ul.empty();
      $sidebar_ul.animate({
        height: ul.length*20 + 'px',
      }, 500, function () {
        $.each(ul, function (i, j) {
          j.appendTo($sidebar_ul);
        });
      });
    }

    var $content = $('body .container-fluid > .content');
    var $content_row = $content.find('.row');

    this.use('Mustache', 'ms');

    this.get('#!/', function (context) {
      set_sidebar_h2('Docky');

      var ul_raw = [
        {name: 'what is docky',
         url: '#!/about'},
        {name: 'projects',
         url: '#!/projects'},
      ]
      var ul = []

      $.each(ul_raw, function (i, j) {
        o = context.render('/media/template/sidebar_ul.ms', j);
        ul[i] = o;
      });

      set_sidebar_ul(ul);
    });

    this.get('#!/projects', function (context) {
      set_sidebar_h2('Projects')

      context.load('/projects')
             .then(function (json) {
               var ul = [];
               $.each(json, function (i, j) {
                 j.url = '#!/projects/' + j.name;
                 o = context.render('/media/template/sidebar_ul.ms', j);
                 ul[i] = o;
               })
               set_sidebar_ul(ul);

               // set as a signal
               docky.last = context.params.path;
             });
    });


    this.get('#!/projects/:name', function (context) {
      /*
      context.log(docky.last);
      if (docky.last != '#!/projects') {
        context.log('not compatable, run ');
        docky.run('#!/projects');
      }
      */

      context.load('/projects/name:' + context.params.name)
             .then(function (json) {
                context.log(json.name);
                json.url = '#!/projects/' + context.params.name + '/rs';
                o = context.render('/media/template/content_project.ms', json);
                context.log(o);
                //$content_row.append(o);
                $content_row.empty();
                o.appendTo($content_row);
             });
    });
  });

  $(function () {
    docky.run('#!/');
  });
})(jQuery);

$(function () {
  $.meow({
    message: 'ofck',
  })



})
