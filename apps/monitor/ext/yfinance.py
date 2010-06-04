import csv
from urllib2 import urlopen


class YahooSymbol(object):
    """ Yahoo finance symbol """
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = float(price)


class YahooFinance(dict):
    """ Yahoo finance API query """
    def query(self, symbols):
        """ Download and parse content """
        url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=snl1' % \
            '+'.join(symbols)
        reader = csv.reader(urlopen(url))
        for line in reader:
            self[line[0]] = YahooSymbol(*line)
