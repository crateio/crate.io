$("a[rel='tooltip']").tooltip();

$("a.disable-link").click(function(e) {
    e.preventDefault();
});

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
