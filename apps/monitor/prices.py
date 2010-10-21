import stomp

from ext.yfinance import YahooSymbol


class PriceConsumer(object):
    def __init__(self):
        self.conn = stomp.Connection()
        self.conn.set_listener('', self)
        self.conn.start()
        self.conn.connect()
        self.conn.subscribe(destination='/queue/prices', ack='auto')
        self.prices = {}

    def add_symbol(self, symbol):
        self.conn.send(
            "ADD %s" % item.symbol, destination="/prices/add")

    def get_symbol(self, symbol):
        return self.prices.get(symbol)

    def on_message(self, headers, message):
        parts = message.split(",")
        if not len(parts) == 3:
            return
        symbol, name, price = parts
        try:
            price = float(price)
        except TypeError:
            return
        else:
            self.prices[symbol] = YahooSymbol(symbol, name, price)

consumer = PriceConsumer()

