// depends on bootstrap3-typeahead.min.js

function spellcorrect(idElement, query) {
    var timeout;
    $(idElement).typeahead({
            minLength: 3,
            matcher: function(item) {
                // return the whole list, because service does matching already
                return true
            },
            source: function(query, process) {
                if (timeout) {
                    clearTimeout(timeout);
                }
                timeout = setTimeout(function() {
                    $.ajax({
                        url: '/suggest',
                        data: {
                            q: query
                        },
                        dataType: 'json'
                    }).success(function(data) {
                        process(data)
                    });
                }, 1000);
            }
        });
}


