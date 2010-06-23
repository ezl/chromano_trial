import csv
from urllib2 import urlopen


class YahooSymbol(object):
    """ Yahoo finance symbol """
    def __init__(self, symbol, name, price):
        self.symbol = symbol
        self.name = name
        self.price = float(price)


class YahooFinance(dict):
    """ Yahoo finance API query """
    def query_multiple(self, symbols):
        """ Download and parse content """
        if not symbols:
            return
        url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=snl1' % \
            '+'.join(symbols)
        reader = csv.reader(urlopen(url))
        for line in reader:
            self[line[0]] = YahooSymbol(*line)

    def query_single(self, symbol):
        """ Shortcut method """
        self.query_multiple([symbol])
        return self[symbol]

    def __getitem__(self, name):
        """ Normalize symbol names """
        return dict.__getitem__(self, name.upper())
