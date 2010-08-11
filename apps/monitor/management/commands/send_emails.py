from datetime import datetime

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.core.mail import send_mail
from django.template import Context, loader

from monitor.models import UserProfile


class Command(NoArgsCommand):
    help = 'Send out emails to registered users'

    def handle_noargs(self, **options):
        """ Check account state and send notifications """
        now = datetime.now()

        # check trial period for paid accounts
        for profile in UserProfile.objects.all().select_related():
            # skip free accounts
            if profile.plan.free:
                continue

            # days since registration
            days = (now - profile.user.date_joined).days
            if days == settings.TRIAL_WARNING:
                self.send(profile.user, 'email_trial.txt', dict(
                    days_passed=settings.TRIAL_WARNING,
                    days_trial=settings.TRIAL_PERIOD,
                    days_left=settings.TRIAL_PERIOD - settings.TRIAL_WARNING,
                ))

    def send(self, user, template, context):
        """ Send email to the user """
        tpl = loader.get_template(template)
        ctx = Context({'user': user, 'data': context})
        subject, message = tpl.render(ctx).split('\n', 1)
        send_mail(subject=subject, message=message,
            from_email=settings.ALERTS_EMAIL,
            recipient_list=[user.username])
