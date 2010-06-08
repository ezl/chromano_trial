from django.contrib import admin

from models import SubscriptionPlan, FinancialInstrument, PriceWatch


class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_price_watches',
        'allow_email_alerts', 'limit_email_alerts',
        'allow_phone_alerts', 'limit_phone_alerts',
        'billing_period_price', 'billing_period_length')


class FinancialInstrumentAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'last_price', 'last_update')
    search_fields = ('symbol', 'name')


class PriceWatchAdmin(admin.ModelAdmin):
    list_display = ('user', 'instrument', 'active',
        'lower_bound', 'upper_bound')
    search_fields = ('user', 'instrument')


# register administration components
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(FinancialInstrument, FinancialInstrumentAdmin)
admin.site.register(PriceWatch, PriceWatchAdmin)
