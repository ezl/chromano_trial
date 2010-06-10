from django.contrib.auth.models import User
from django.db import models


class SubscriptionPlan(models.Model):
    """ User subscription options """
    name = models.CharField("Plan name", max_length=100)
    description = models.TextField("Description", blank=True)
    max_price_watches = models.IntegerField("Max.monitors")
    allow_email_alerts = models.BooleanField("Email alerts")
    limit_email_alerts = models.IntegerField("Email alerts limit", default=0)
    allow_phone_alerts = models.BooleanField("SMS alerts")
    limit_phone_alerts = models.IntegerField("SMS alerts limit", default=0)
    billing_period_price = models.IntegerField("Price")
    billing_period_length = models.IntegerField("Period (days)")

    def __unicode__(self):
        return 'Plan: %s' % self.name


class FinancialInstrument(models.Model):
    """ Stock symbol """
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    last_price = models.FloatField()
    last_update = models.DateTimeField(auto_now=True)

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
    position = models.IntegerField(default=0)

    class Meta:
        #unique_together = [('user', 'instrument')]
        verbose_name_plural = 'price watches'

    def __unicode__(self):
        return '%s: (%s<%s<%s)' % (self.user, self.lower_bound or '0',
            self.instrument, self.upper_bound or 'inf')


class UserProfile(models.Model):
    """ User resource usage """
    user = models.ForeignKey(User)
    plan = models.ForeignKey(SubscriptionPlan)

    phone_number = models.CharField(max_length=20, null=True, blank=True)
    phone_verified = models.BooleanField()
    phone_activation_string = models.CharField(max_length=10, blank=True)

    count_email_alerts = models.IntegerField("Email alerts remaining", default=0)
    count_phone_alerts = models.IntegerField("SMS alerts remaining", default=0)
    received_email_alerts = models.IntegerField("Email alerts received", default=0)
    received_phone_alerts = models.IntegerField("SMS alerts received", default=0)

    @property
    def count_watches(self):
        """ Number of available monitors """
        max_ = self.plan.max_price_watches
        if not max_:
            return 9999
        qs = PriceWatch.objects.filter(user=self.user, active=True)
        return max_ - qs.count()

    def reset(self):
        """ Reset values to defaults """
        self.count_email_alerts = (self.plan.limit_email_alerts or -1) \
            if self.plan.allow_email_alerts else 0
        self.count_phone_alerts = (self.plan.limit_phone_alerts or -1) \
            if self.plan.allow_phone_alerts else 0
        self.received_email_alerts = 0
        self.received_phone_alerts = 0
        self.save()
