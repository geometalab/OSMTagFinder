var newRender = function(items) {
    var that = this

    items = $(items).map(function (i, item) {
      i = $(that.options.item).attr('data-value', item)
      i.find('a').html(that.highlighter(item))
      return i[0]
    })

    this.$menu.html(items)
    return this
};
$.fn.typeahead.Constructor.prototype.render = newRender;

$.fn.typeahead.Constructor.prototype.select = function() {
    var val = this.$menu.find('.active').attr('data-value');
    if (val) {
      this.$element
        .val(this.updater(val))
        .change();
    }
    return this.hide()
};
