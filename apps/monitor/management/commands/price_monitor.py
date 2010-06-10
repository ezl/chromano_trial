from datetime import datetime

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.core.mail import send_mail

from monitor.models import PriceWatch, UserProfile
from monitor.ext.yfinance import YahooFinance
from monitor.ext.gvoice import GoogleVoiceLogin, TextSender


class Command(NoArgsCommand):
    help = 'Checks to see if any PriceWatch should be triggered'

    def handle_noargs(self, **options):
        """ Check prices and send notifications """
        # login to google voice
        print 'Logging in to Google Voice...'
        user_, pass_ = settings.GOOGLE_VOICE_USER, settings.GOOGLE_VOICE_PASS
        self.gvoice = GoogleVoiceLogin(user_, pass_)
        
        # load latest prices
        qs = PriceWatch.objects.filter(active=True)
        instruments = set([item.instrument for item in qs])
        
        print 'Fetching data from Yahoo Finance...'
        yapi = YahooFinance()
        yapi.query_multiple([inst.symbol for inst in instruments])
        
        # save updated prices to the database
        get_price = lambda inst: yapi[inst.symbol].price
        for inst in instruments:
            inst.last_price = get_price(inst)
            inst.save()

        # check boundaries
        print 'Processing %d items' % qs.count()
        for item in qs:
            price = get_price(item.instrument)
            if item.lower_bound and price < item.lower_bound:
                self.send_alerts(item, price, 'L')
            if item.upper_bound and price > item.upper_bound:
                self.send_alerts(item, price, 'U')

    def send_alerts(self, item, price, type_):
        """ Send alert (email and phone) """
        try:
            profile = UserProfile.objects.get(user=item.user)
        except UserProfile.DoesNotExist:
            return  # admin account

        # format message
        if type_ == 'L':
            message = "%s price %s, below your price (%s)" % \
                (item.instrument, price, item.lower_bound)
        if type_ == 'U':
            message = "%s price %s, above your price (%s)" % \
                (item.instrument, price, item.upper_bound)
        
        # send email alert
        if profile.count_email_alerts and profile.user.email:
            # send message
            try:
                send_mail(subject=message, message=message,
                    from_email=settings.ALERTS_EMAIL,
                    recipient_list=[profile.user.email])
            except Exception, e:
                print 'Mailer fail: %s / %s' % (profile.user.email, str(e))
            # update counters
            if profile.count_email_alerts > 0:
                profile.count_email_alerts -= 1
                profile.received_email_alerts += 1
                profile.save()
        
        # send phone alert
        if profile.count_phone_alerts and profile.phone_verified:
            # send message
            try:
                sender = TextSender(self.gvoice.opener, self.gvoice.key)
                sender.text = message
                sender.send_text(profile.phone_number)
            except Exception, e:
                print 'Sender fail: %s / %s' % (profile.phone_number, str(e))
            # update counters
            if profile.count_phone_alerts > 0:
                profile.count_phone_alerts -= 1
                profile.received_phone_alerts += 1
                profile.save()
        
        # update item record
        item.triggered = datetime.now()
        item.active = False
        item.save()
