function switchLanguageTo(lang, sheet){
    document.getElementById('langstyle').setAttribute('href', sheet);
    document.documentElement.lang=lang;
    $.ajax({url:'/lang', type:'POST', data:{lang:lang}});
}
