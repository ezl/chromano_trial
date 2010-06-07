
jQuery(function($) {
    $('.grid-watch ul').sortable();

    // symbol template (should be changed if template is altered)
    function format(v) {
        if (v == null)
            return '---';
        if (typeof v == 'number')
            return v.toFixed(4).replace(/\.?0*$/, '');
        return v;
    }

    function createItem(data) {
        var tpl = '<li id="w{{ id }}" class="ui-state-default ui-corner-all">' +
            '<table><tr>' +
            '<th scope="row" class="symbol">' +
            '<a href="/monitor/edit/{{ id }}/active" class="icon icon-on toggle"></a>' +
            ' {{ symbol }}</th>' +
            '<td><div class="editable lower">{{ lower_bound }}</div></td>' +
            '<td><div class="price">{{ price }}</div></td>' +
            '<td><div class="editable upper">{{ upper_bound }}</div></td>' +
            '<td><a href="/monitor/del/{{ id }}" class="icon icon-trash remove"></a></td>' +
            '</tr></table>' +
            '</li>';
        var html = tpl.replace(/{{\s*(\w+)\s*}}/g, function(m, k) { return format(data[k]) }, tpl),
            el = $(html).hide().prependTo($('.grid-watch ul')).fadeIn('slow');
        return el;
    }

    // symbol toggle
    $('.grid-watch .toggle').live('click', function(ev) {
        ev.preventDefault();
        var link = $(ev.target);
        $.get(link.attr('href'), function(data) {
            if (!data) return;
            link.removeClass('icon-on').removeClass('icon-off')
                .addClass(data.value ? 'icon-on' : 'icon-off');
        }, 'json');
    });

    // symbol delete
    $('.grid-watch .remove').live('click', function(ev) {
        ev.preventDefault();
        var link = $(ev.target), item = link.parents('li');
        item.removeClass('ui-state-default').addClass('ui-state-disabled');
        $.get(link.attr('href'), function(data) {
            if (!data) return;
            item.fadeOut('slow', function() { item.remove() });
        }, 'json');
    });

    // symbol add
    $('.add-watch form').submit(function(ev) {
        ev.preventDefault();
        if (!symbolInput.val())
            return;
        var form = $(this);
        $.post(form.attr('action'), form.serialize(), function(data) {
            if (!data || data.error)
                return;
            form.find('.name, .price').html('&nbsp;');
            form.find(':input').val('') // reset values
                .first().focus(); // focus first element
            createItem(data);
        }, 'json');
    });

    // symbol check
    var checkTimeout = null, checkFailed = {}, checkLast = null,
        priceDisplay = $('.add-watch .price'),
        nameDisplay = $('.add-watch .name'),
        symbolInput = $('#id_symbol');

    function checkLoad() {
        var value = symbolInput.val();
        if (!value.match(/^[\w\.]+$/) || checkFailed[value] || checkLast == value)
            return;
        priceDisplay.html('<div class="icon price-loader"></div>');
        nameDisplay.html('&nbsp;');
        $.get('/monitor/check/' + value, function(data) {
            if (symbolInput.val() != value)
                return;
            if (!data || data.error) {
                if (data)
                    checkFailed[value] = true;
                priceDisplay.html('&nbsp;');
            } else {
                priceDisplay.html(format(data.price));
                nameDisplay.html(data.name);
            }
            checkLast = value;
        }, 'json');
    }

    function checkSymbol() {
        clearTimeout(checkTimeout);
        checkTimeout = setTimeout(checkLoad, 500);
    }
    $('#id_symbol').keypress(checkSymbol).change(checkSymbol);
});
