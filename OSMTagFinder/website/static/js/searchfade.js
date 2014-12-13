function searchfade(found, query) {
    $(function() {
        if(found >= 0 && query) { // truthy check
            $('#jumbotron_search').hide();
            $('#nav_footer').hide();
            $('#navbarsearch-ingroup').show();
            $('.background-footer').hide();
        }
        else {
            $('#jumbotron_search').show();
            $('#nav_footer').show();
            $('#navbarsearch-ingroup').hide();
            $('.background-footer').show();
        }

        if($(window).width() > 770 && !query) {
            $('#nav_footer').show();
            //$('.background-footer').show();
        }
        else {
            $('#nav_footer').hide();
            //$('.background-footer').hide();
        }

    });
}