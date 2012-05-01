$(function() {
  $(".json-form button[type=submit]").click(function() {
    var form = $(this).closest("form");

    $.post(
        form.attr("action"),
        form.serialize(),
        function(data){
            // @@@ Consider Passing a Callback in, instead of hardcoded
            if (data.success) {
                window.location.reload(true);
            }
            else {
                // @@@ Do Something Smarter Here; What?
                alert(data.message);
            }
        }
    );

    $(this).addClass("disabled");
    form.find(".progress").show();

    return false;
  });

  $("*[data-onclick=submit]").click(function() {
    var form = $(this).closest("form");

    $.post(
      form.attr("action"),
      form.serialize(),
      function(data) {
        // @@@ Consider Passing a Callback in, instead of hardcoded
        if (data.success) {
          window.location.reload(true);
        }
        else {
          // @@@ Do Something Smarter Here; What?
          alert(data.message);
        }
      }
    );

    $(this).replaceWith('<a><div class="progress progress-striped active"><div class="bar" style="width: 100%;"></div></div></a>');

    return false;
  });
});

$("a[rel='tooltip']").tooltip();

$("a.disable-link").click(function(e) {
    e.preventDefault();
});

// fix sub nav on scroll
var $win = $(window),
    $nav = $('.subnav'),
    navTop = $('.subnav').length && $('.subnav').offset().top - 40,
    isFixed = 0;

processScroll();

// hack sad times - holdover until rewrite for 2.1
$nav.on('click', function () {
    if (!isFixed) setTimeout(function () {  $win.scrollTop($win.scrollTop() - 47); }, 10);
});

$win.on('scroll', processScroll);

function processScroll() {
    var i, scrollTop = $win.scrollTop();

    if (scrollTop >= navTop && !isFixed) {
        isFixed = 1;
        $nav.addClass('subnav-fixed');
    } else if (scrollTop <= navTop && isFixed) {
        isFixed = 0;
        $nav.removeClass('subnav-fixed');
    }
}

// Page Specific
fayer.on("release-detail", function(){
    $(document).ready(function (){
        $("a.favoriter").click(function(e){
            e.preventDefault();

            var that = this;

            $.post($(this).attr("href"), function(data){
                if (data.action == "favorite") {
                    $(that).find("img").each(function(){
                        $(this).attr("src", $(this).data("favoriteImg"));
                    });
                }
                else if (data.action == "unfavorite") {
                    $(that).find("img").each(function(){
                        $(this).attr("src", $(this).data("unfavoriteImg"));
                    });
                }
            });
        });
    });
});
