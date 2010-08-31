import httplib
import datetime
import re
import simplejson as json
from threading import Thread
import logging

from monitor.models import FinancialInstrument
from yfinance import YahooSymbol

import os
path = os.getcwd()
LOG_FILENAME = "%s/stream.log" % path
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

class YahooFinanceStream(Thread):
    """ Streaming data implementation """
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.symbols = {}
        self.conn = None
        self.data = ''
        self.active = True

    def connect(self):
        logging.debug(".CONNECT")
        symbols_slug = ','.join(self.symbols.keys()) or 'A'
        self.conn = httplib.HTTPConnection("streamerapi.finance.yahoo.com")
        self.conn.request("GET", "/streamer/1.0?s=%s&k=%s&" \
            "callback=parent.yfs_u1f&mktmcb=parent.yfs_mktmcb&" \
            "gencallback=parent.yfs_gencb" % (symbols_slug, 'l90'))
        self.resp = self.conn.getresponse()
        self.data = ''
        logging.debug(".FINISHED CONNECT")

    def run(self):
        while self.active:
            try:
                self.connect()
                while True:
                    char = self.resp.read(1)
                    self.data += char
                    if char == '>':
                        self.parse_line(self.data)
                        self.data = ''
            except httplib.HTTPException, e:
                logging.debug("HTTPException. Should  try to reconnect.")
                pass  # re-connect
            except Exception, e:
                logging.debug("UNHANDLED EXCEPTION")
                logging.debug(e)
                self.active = False

    def parse_line(self, line):
        m = re.search("\((.*?)\)", line)
        if not m:
            return
        valid = re.sub("(\w+):", '"\\1":', m.group(1))
        data = json.loads(valid)

        if "unixtime" in data.keys():
            logging.debug("%s | HEARTBEAT: %s" % (datetime.datetime.now(), data["unixtime"]))
            return

        for k, v in data.items():
            price = v['l90']
            logging.debug("%s | %s: %s" % (datetime.datetime.now(), k, price))
            self.symbols[k].price = price
            item = FinancialInstrument.objects.get(symbol=k)
            item.last_price = price
            item.save()

    def add_symbol(self, item):
        self.symbols[item.symbol] = \
            YahooSymbol(item.symbol, item.name, item.last_price)
        if self.conn:
            self.conn.close()


# create thread instance
yahoo_feed = YahooFinanceStream()
for item in FinancialInstrument.objects.all():
    yahoo_feed.add_symbol(item)
yahoo_feed.start()

# available data items
yahoo_items = {
    'a00': 'ask price',
    'b00': 'bid price',
    'g00': "day's range low",
    'h00': "day's range high",
    'j10': 'market cap',
    'v00': 'volume',
    'a50': 'ask size',
    'b60': 'bid size',
    'b30': 'ecn bid',
    'o50': 'ecn bid size',
    'z03': 'ecn ext hr bid',
    'z04': 'ecn ext hr bid size',
    'b20': 'ecn ask',
    'o40': 'ecn ask size',
    'z05': 'ecn ext hr ask',
    'z07': 'ecn ext hr ask size',
    'h01': "ecn day's high",
    'g01': "ecn day's low",
    'h02': "ecn ext hr day's high",
    'g11': "ecn ext hr day's low",
    't10': 'last trade time, will be in unix epoch format',
    't50': 'ecnQuote/last/time',
    't51': 'ecn ext hour time',
    't53': 'RTQuote/last/time',
    't54': 'RTExthourQuote/last/time',
    'l10': 'last trade',
    'l90': 'ecnQuote/last/value',
    'l91': 'ecn ext hour price',
    'l84': 'RTQuote/last/value',
    'l86': 'RTExthourQuote/last/value',
    'c10': 'quote/change/absolute',
    'c81': 'ecnQuote/afterHourChange/absolute',
    'c60': 'ecnQuote/change/absolute',
    'z02': 'ecn ext hour change',
    'z08': 'ecn ext hour change',
    'c63': 'RTQuote/change/absolute',
    'c85': 'RTExthourQuote/afterHourChange/absolute',
    'c64': 'RTExthourQuote/change/absolute',
    'p20': 'quote/change/percent',
    'c82': 'ecnQuote/afterHourChange/percent',
    'p40': 'ecnQuote/change/percent',
    'p41': 'ecn ext hour percent change',
    'z09': 'ecn ext hour percent change',
    'p43': 'RTQuote/change/percent',
    'c86': 'RTExtHourQuote/afterHourChange/percent',
    'p44': 'RTExtHourQuote/change/percent',
}
