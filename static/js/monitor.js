
jQuery(function($) {
    // symbol add
    $('.add-watch form').submit(function(ev) {
        ev.preventDefault();
    });

    // symbol check
    var checkTimeout = null, checkFailed = {},
        priceDisplay = $('.add-watch .price'),
        nameDisplay = $('.add-watch .name'),
        symbolInput = $('#id_symbol');

    function formatPrice(v) {
        var n = Math.log(v) / Math.log(10);
        return v.toFixed(4 - Math.floor(n));
    }

    function checkLoad() {
        var value = symbolInput.val();
        if (!value.match(/^[\w\.]+$/) || checkFailed[value])
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
                priceDisplay.html(formatPrice(data.price));
                nameDisplay.html(data.name);
            }
        }, 'json');
    }

    function checkSymbol() {
        clearTimeout(checkTimeout);
        checkTimeout = setTimeout(checkLoad, 500);
    }
    $('#id_symbol').keypress(checkSymbol).change(checkSymbol);
});
