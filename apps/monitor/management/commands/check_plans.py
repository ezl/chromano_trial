from django.conf import settings
from django.core.management.base import NoArgsCommand

from monitor.models import SubscriptionPlan
from pycheddar import CheddarGetter as CG, Plan


class Command(NoArgsCommand):
    help = 'Check payment plan consistency on CheddarGetter'

    def handle_noargs(self, **options):
        """ Compare existing payment plans """

        # authorize on remote server
        CG.auth(settings.CHEDDAR_GETTER_USER, settings.CHEDDAR_GETTER_PASS)
        CG.set_product_code(settings.CHEDDAR_GETTER_PRODUCT)

        # fetch plans
        plans_remote = Plan.all()
        plans_map = dict([(x.code, x) for x in plans_remote])
        plans_local = SubscriptionPlan.objects.all()

        # compare by name
        for plan in plans_local:
            plan_code = plan.name.upper()
            is_match = plan_code in plans_map
            print plan.name, '..', 'match' if is_match else 'NO MATCH'
