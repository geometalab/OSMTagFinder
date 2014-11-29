// depends on bootstrap3-typeahead.min.js

function spellcorrect(idElement, query, lang) {
    $(idElement).typeahead({
            minLength: 3,
            matcher: function(item) {
                // return the whole list, because service does matching already
                return true
            },
            source: function(query, process) {
                $.ajax({
                        url: '/api/suggest',
                        data: {
                            q: query,
                            lang: lang
                        },
                        dataType: 'json'
                    }).success(function(data) {
                        process(data)
                    });
            }
        });
}


