
jQuery(function($) {
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

    // periodic updates
    function updatePrices() {
        var items = $('.grid-watch .symbol'),
            symbols = items.map(function(k,v) { return $.trim($(v).text()) }).toArray();
        $.get('/monitor/check/' + symbols.join(','), function(data) {
            $.each(data.data, function(k, v) {
                $(items[k]).siblings().find('.price').html(format(v.price));
            });
        }, 'json');
    }
    setInterval(updatePrices, 62 * 1000);

    // edit limit values
    var editing = null;
    $('.grid-watch .editable').live('click', function(ev) {
        if (ev.target.tagName == 'INPUT')
            return;
        if (editing)
            editing.blur();

        var el = $(ev.target),
            id = el.parents('li').attr('id').substring(1),
            value = parseFloat(el.html()) || null,
            input = $('<input type="text">').val(value || '');
        el.html('').append(input);
        input.focus();
        editing = input;

        input.blur(function() {
            var v = parseFloat(this.value) || null;
            if (v < 0) v = null;
            if (v != value) {
                var field = el[0].className.split(' ').pop();
                $.get('/monitor/edit/' + id + '/' + field + '?value=' + (v || '0'));
            }
            el.html(format(v));
            editing = null;
        });
        input.keypress(function(ev) {
            if (ev.which == 13)
                this.blur();
        });
    });

    // sort columns
    function sortHeader(ev, index, desc) {
        ev.preventDefault();
        var a = $('.grid-watch li').toArray(),
            f = index ? function(v) { return parseFloat(v) || 0 } : $.trim,
            txt = function(e) { return $('th,td', e).eq(index).text() },
            val = !desc ? 1 : -1;
        a.sort(function(e1, e2) {
            var v1 = f(txt(e1)), v2 = f(txt(e2));
            if (v1 == v2) return 0;
            return v1 < v2 ? val : -val;
        });
        $(a).each(function() {
            $(this).prependTo(this.parentNode);
        });
        updatePosition();
    }
    $('.grid-watch .header th').each(function(k) {
        var el = $(this), label = el.html(),
            sort_asc = $('<a href="#">')
                .html(label + ' <small>&#9660;</small>')
                .click(function(ev) { sortHeader(ev, k) }),
            sort_desc = $('<a href="#">')
                .html(' <small>&#9650;</small>')
                .click(function(ev) { sortHeader(ev, k, true) });
        if (label)
            el.html('').append(sort_asc, sort_desc);
    });

    // symbol position
    function updatePosition() {
        var list = [];
        $('.grid-watch li').each(function() {
            list.push(this.id.substring(1));
        });
        $.get('/monitor/pos/?order=' + list.join(','));
    }
    $('.grid-watch ul').sortable({
        update: updatePosition,
        start: function() { if (editing) editing.blur() }
    });

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
            if (data.error)
                return $('p', form).html('<em>' + data.error + '</em>');
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
            if (data.error) {
                checkFailed[value] = true;
                priceDisplay.html('&nbsp;');
            } else {
                info = data.data[0];
                priceDisplay.html(format(info.price));
                nameDisplay.html(info.name);
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
