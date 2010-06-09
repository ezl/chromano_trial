from django.contrib import admin

from models import SubscriptionPlan, FinancialInstrument, \
    PriceWatch, UserCounter


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


class UserCounterAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan',
        'count_email_alerts', 'count_phone_alerts')
    search_fields = ('user',)
    filters = ('plan',)


# register administration components
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(FinancialInstrument, FinancialInstrumentAdmin)
admin.site.register(PriceWatch, PriceWatchAdmin)
admin.site.register(UserCounter, UserCounterAdmin)
