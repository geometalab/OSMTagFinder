function ajaxSuggest(liElementEN, liElementDE, query) {
    var timeout;
    if (timeout) {
        clearTimeout(timeout);
    }
    timeout = setTimeout(function() {
        $.ajax({
            url: '/suggest',
            data: {
                query: query
            },
            dataType: 'json'
        }).success(function(data) {
            if(data.length <= 0) {
                var noSuggestionsEN = 'No suggestions could be found.';
                var noSuggestionsDE = 'Es konnten keine Vorschläge gefunden werden.';
                liElementEN.innerHTML = liElementEN.innerHTML + noSuggestionsEN.italics();
                liElementDE.innerHTML = liElementDE.innerHTML + noSuggestionsDE.italics();
                return;
            }
            var i = 0;
            for(var key in data) {
                if(data.hasOwnProperty(key)) {
                    var dataElement = data[key];
                    var aElementEN = document.createElement('a');
                    var aElementDE = document.createElement('a');
                    
                    aElementEN.href =  '/search?query=' + dataElement;
                    aElementEN.innerHTML = dataElement;
                    aElementDE.href =  '/search?query=' + dataElement;
                    aElementDE.innerHTML = dataElement;
                    
                    liElementEN.appendChild(aElementEN);
                    liElementDE.appendChild(aElementDE);
                    if((i != data.length - 1)) {
                        liElementEN.appendChild(document.createTextNode(', '));
                        liElementDE.appendChild(document.createTextNode(', '));
                    }
                    else {
                        liElementEN.appendChild(document.createTextNode('?'));
                        liElementDE.appendChild(document.createTextNode('?'));
                    }
                }
                i++;
            }
        });
    }, 1000);
}
