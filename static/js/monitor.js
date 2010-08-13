
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
        var tpl = '<li id="w{{ id }}">' +
            '<table><tr>' +
            '<th scope="row" class="tab-active">' +
            '<a href="/monitor/edit/{{ id }}/active" class="center icon-on toggle"></a>' +
            '</th>' +
            '<td class="symbol tab-symbol">{{ symbol }}</td>' +
            '<td class="tab-lower"><div class="editable lower">{{ lower_bound }}</div></td>' +
            '<td class="tab-price"><div class="price">{{ price }}</div></td>' +
            '<td class="tab-upper"><div class="editable upper">{{ upper_bound }}</div></td>' +
            '<td class="tab-alerts"><a href="/monitor/edit/{{ id }}/alert_phone" class="icon alert-phone {{ alert_phone }}"></a>' +
            '<a href="/monitor/edit/{{ id }}/alert_email" class="icon alert-email {{ alert_email }}"></a></td>' + 
            '<td class="tab-remove"><a href="/monitor/del/{{ id }}" class="icon icon-trash remove"></a></td>' +
            '</tr></table>' +
            '</li>';
        $('#help-text').hide();
        var html = tpl.replace(/{{\s*(\w+)\s*}}/g, function(m, k) { return format(data[k]) }, tpl),
            el = $(html).hide().prependTo($('.grid-watch ul')).fadeIn('slow');
        return el;
    }

    // update label and display warning
    function updateCountLabel(delta) {
        var el = $('#watch-count'), value = parseInt(el.html()) + delta,
            elMax = $('#watch-max'), valueMax = parseInt(elMax.html()),
            count = valueMax - value;
        if (valueMax) {
            $('#warn-limit').toggle(valueMax - value < 5);
            $('#watch-near').toggle(!!count);
            $('#watch-limit').toggle(!count);
        }
        el.html(value);
        return value;
    }

    // periodic updates
    function updatePrices() {
        var items = $('.grid-watch .symbol'),
            symbols = items.map(function(k, v) { return $.trim($(v).text()) }).toArray(),
            groups = {};
        if (!items.length) return;
        $.each(symbols, function(k, v) {
            if (!groups[v])
                groups[v] = [];
            groups[v].push(items[k]);
        });
        $.get('/monitor/check/' + symbols.join(','), function(data) {
            $.each(data.data, function(k, v) {
                var selector = $(groups[v.symbol]).siblings('.tab-price').find('.price');
                var oldPrice = +selector.html();
                var newPrice = v.price;
                selector.html(format(newPrice));
                var a;
                if (newPrice > oldPrice) a = '#dfd';
                else if (newPrice < oldPrice) a = '#fdd';
                //else if (Math.random() < 1/3) a = '#dfd'; // for debugging
                if (a) {
                  selector.css('background-color',a)
                  .animate({'background-color':'#fff'},2000,function(){
                      $(this).css('background-color','');
                  });
                }
            });
            setTimeout(updatePrices,2 * 1000);
        }, 'json');
    }
    updatePrices();

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
            if (!compareToPrice(v, el)) v = value;
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

    function displayError(el, message) {
        el.find('div.floater').remove();  //flush any old floaters
        var floater = $('<div class="floater ui-state-error ui-corner-all">'+message+'</div>').css('opacity', 0.9)
            .appendTo(el).click(function() {
                floater.fadeOut('slow', function() { floater.remove() });
            });
    }
    function compareToPrice(value, el) {
        el.siblings('div.floater').remove();  //flush any old floaters

        // compare value to price
        var item = el.parents('li'),
            price = parseFloat(item.find('.price').html()),
            upper = el.hasClass('upper'), lower = !upper;
        if ((upper && value > price) || (lower && value < price) || value == null)
            return true;

        // display floating error
        var msg = (upper ? 'Value is below the price' : 'Value is above the price');
        displayError(el.parent(), msg);
    }
    window.test = compareToPrice;

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
    $('header.grid-watch th:not(.nosort)').each(function(k) {
        var el = $(this), label = el.text(),
            sort_asc = $('<a href="#">' + label + ' <small>&#9660;</small></a>')
                .click(function(ev) { sortHeader(ev, k) }),
            sort_desc = $('<a href="#"> <small>&#9650;</small></a>')
                .click(function(ev) { sortHeader(ev, k, true) });
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
            if (data.breach) {
                var msg = data.breach + ' boundary is breached';
                return displayError(link.parents('li'), msg);
            }
            link.removeClass('icon-on').removeClass('icon-off')
                .addClass(data.value ? 'icon-on' : 'icon-off');
            updateCountLabel(data.value ? 1 : -1);
        }, 'json');
    });

    $('.grid-watch [class^="alert-"]').click(function(ev) {
        ev.preventDefault();
        var link = $(ev.target);
        $.get(link.attr('href'), function(data) {
            if (!data) return;
            if (data.alert) {
                var msg = 'No configured ' + data.alert;
                return displayError(link.parents('li'), msg);
            }
            link.removeClass('true').removeClass('false')
                .addClass(data.value ? 'true' : 'false');
        }, 'json');
    });
    // symbol delete
    $('.grid-watch a.remove').live('click', function(ev) {
        ev.preventDefault();
        var link = $(ev.target), item = link.parents('li');
        item.removeClass('ui-state-default').addClass('ui-state-disabled');
        $.get(link.attr('href'), function(data) {
            if (!data) return;
            item.fadeOut('medium', function() {
              item.remove();
              if (!$('div.grid-watch ul > li').length) $('#help-text').fadeIn();
            });
            if (item.find('.icon-on').length)
                updateCountLabel(-1);
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
                return $('p', form).html('<div class="errorlist">' + data.error + '</div>');
            form.find('.name').html('');
            form.find('input').val('') // reset values
                .first().focus(); // focus first element
            createItem(data);
            updateCountLabel(1);
        }, 'json');
    });

    // symbol check
    var checkTimeout = null, checkFailed = {}, checkLast = null,
        priceDisplay = $('.add-watch .price'),
        priceDisplayLoader = $('.add-watch .price-loader'),
        nameDisplay = $('.add-watch .name'),
        symbolInput = $('#id_symbol');

    function checkLoad() {
        var value = symbolInput.val();
        if (!value.match(/^[\w\.]+$/) || checkFailed[value] || checkLast == value)
            return;
        priceDisplayLoader.show();
        priceDisplay.hide();
        nameDisplay.html('&nbsp;');
        $.get('/monitor/check/' + value, function(data) {
            if (symbolInput.val() != value)
                return;
            if (data.error) {
                checkFailed[value] = true;
                priceDisplay.val('');
            } else {
                info = data.data[0];
                priceDisplay.val(format(info.price));
                nameDisplay.html(info.name);
            }
            priceDisplayLoader.hide();
            priceDisplay.show();
            checkLast = value;
        }, 'json');
    }

    function checkSymbol() {
        clearTimeout(checkTimeout);
        checkTimeout = setTimeout(checkLoad, 500);
    }
    $('#id_symbol').keypress(checkSymbol).change(checkSymbol);
});
