from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail

from monitor.ext.gvoice import TextSender


def send_price_alerts(self, item, price, type_):
    """ Send alert (email and phone) """
    try:
        profile = item.user.get_profile()
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
    if profile.count_email_alerts \
        and profile.user.email and item.alert_email:
        # send message
        try:
            send_mail(subject=message, message=message,
                      from_email=settings.ALERTS_EMAIL,
                      recipient_list=[profile.user.email])
        except Exception, e:
            print 'Mailer fail: %s / %s' % (profile.user.email, str(e))
        # update counters
        else:
            profile.received_email_alerts += 1
            profile.save()

    # send phone alert
    if profile.count_phone_alerts \
        and profile.phone_verified and item.alert_phone:
        # send message
        try:
            sender = TextSender()
            sender.text = message
            sender.send_text(profile.phone_number)
        except Exception, e:
            print 'Sender fail: %s / %s' % (profile.phone_number, str(e))
        # update counters
        else:
            profile.received_phone_alerts += 1
            profile.save()

    # update item record
    item.triggered = datetime.now()
    item.active = False
    item.save()

