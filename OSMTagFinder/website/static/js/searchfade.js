function searchfade() {
    $(function() {
        $(window).scroll(function() {
            // set distance user needs to scroll before we fadeIn navbar
            if ($(this).scrollTop() > 180) {
                $('#navbar-search').fadeIn();
            } else {
                //$('#navbar-search').hide('easing');
                $('#navbar-search').fadeOut();
            }
        });
    });
}