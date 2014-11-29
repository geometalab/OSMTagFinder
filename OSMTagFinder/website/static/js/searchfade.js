function searchfade(found) {
    $(function() {
        if(found > 0) { // truthy check
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

    });
}