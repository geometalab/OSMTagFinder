function setLanguage(lang, sheet) {
    document.getElementById('langstyle').setAttribute('href', sheet);
    document.documentElement.lang=lang;
    $.ajax({url:'/setlang', type:'POST', data:{lang:lang}});
    var hiddenInputs = document.getElementsByClassName('search-lang-param'); // setting language to all hidden input fields for param &lang='..'
    for (var i = 0; i < hiddenInputs.length; ++i) {
        hiddenInputs[i].value = lang;
    }
}

function getLanguage(handleData) {
    $.ajax({url:'/getlang', type:'GET', success:function(data) {
        handleData(data);
    }});
}