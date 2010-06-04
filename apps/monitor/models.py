from django.contrib.auth.models import User
from django.db import models


class SubscriptionPlan(models.Model):
    """ User subscription options """
    name = models.CharField("Plan name", max_length=100)
    description = models.TextField("Description")
    max_price_watches = models.IntegerField("Max.monitors")
    allow_email_alerts = models.BooleanField("Email alerts")
    allow_phone_alerts = models.BooleanField("SMS alerts")
    billing_period_price = models.IntegerField("Price")
    billing_period_length = models.IntegerField("Period (days)")

    def __unicode__(self):
        return 'Plan: %s' % self.name


class FinancialInstrument(models.Model):
    """ Stock symbol """
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    last_price = models.FloatField()
    last_update = models.DateTimeField()

    def __unicode__(self):
        return self.symbol


class PriceWatch(models.Model):
    """ User monitor """
    user = models.ForeignKey(User)
    instrument = models.ForeignKey(FinancialInstrument)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    lower_bound = models.FloatField(null=True, blank=True)
    upper_bound = models.FloatField(null=True, blank=True)
    triggered = models.DateTimeField(null=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = [('user', 'instrument')]
        verbose_name_plural = 'price watches'

    def __unicode__(self):
        return '%s: (%s<%s<%s)' % (self.user, self.lower_bound or '0',
            self.instrument, self.upper_bound or 'inf')
