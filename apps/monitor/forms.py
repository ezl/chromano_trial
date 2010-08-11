import re

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.localflavor.us.forms import USPhoneNumberField, USZipCodeField
#from django.utils.dates import MONTHS

from models import UserProfile
from pycheddar import CheddarGetter as CG, Plan, Customer, Subscription


class RegistrationForm(UserCreationForm):
    """ Registration processing """
    username = forms.EmailField(required=True)
    card_number = forms.CharField(required=False, max_length=20)
    card_holder = forms.CharField(required=False, max_length=50)
    card_expires_month = forms.ChoiceField(required=False,
        choices=[(n, '%02d' % n) for n in xrange(1, 13)])
    card_expires_year = forms.ChoiceField(required=False,
        choices=[(n, n) for n in xrange(2010, 2020)])
    card_cvv = forms.IntegerField(required=False)
    billing_zip_code = USZipCodeField(required=False)

    def __init__(self, free, **kwargs):
        super(RegistrationForm, self).__init__(**kwargs)
        self.free = free

    def clean_card_number(self):
        v = self.cleaned_data['card_number']
        if not self.free and not re.match(r'^(\d{4}\s?){4}$', v):
            raise forms.ValidationError("Oops! Your credit card number doesn't seem valid. Please review our credit card options.")
        return v

    def clean_card_holder(self):
        v = self.cleaned_data['card_holder']
        if not self.free and not re.match(r'^\s*\S+\s\S+', v):
            raise forms.ValidationError("You must enter the name as it appears on the credit card.")
        return v

    def clean_billing_zip_code(self):
        v = self.cleaned_data['billing_zip_code']
        if not self.free and not re.match(r'^[-0-9]{5,10}$', v):
            raise forms.ValidationError("You must enter a valid US zip code.")
        return v

    def subscribe(self, user, plan):
        """ Create remote Customer instance """
        authorize_gateway()
        # fn == firstname, ln == lastname
        fn = ln = "-"
        if plan.free:
            fn, ln = user.email.split("@")
            ln = "@" + ln
        customer = Customer(code=user.id, email=user.username,
            first_name=user.first_name or fn, last_name=user.last_name or ln)
        sub = customer.subscription
        sub.plan = Plan.get(plan.code)
        if not self.free:
            update_subscription(sub, self.cleaned_data, user)
        customer.save()


class ProfileForm(forms.Form):
    """ Profile contacts form """
    email = forms.EmailField(required=False)
    phone = USPhoneNumberField(required=False)

    def save_email(self, user):
        # save email record
        user.email = self.cleaned_data['email']
        user.save()

    def save_phone(self, profile):
        # check if phone has changed
        v = self.cleaned_data['phone']
        if v == profile.phone_number:
            return

        # update profile record
        profile.phone_number = v
        profile.phone_verified = False
        profile.save()


class ActivationForm(forms.Form):
    """ Profile activation form """
    token = forms.RegexField(regex=r'^\w+$')
    phone = USPhoneNumberField(required=False)

    def clean(self):
        data = self.cleaned_data
        try:
            if 'token' in data:
                self.profile = UserProfile.objects.get(
                    phone_number=data['phone'],
                    phone_activation_string=data['token'])
        except UserProfile.DoesNotExist:
            raise forms.ValidationError("The confirmation code doesn't match our records.  Please try again or request a new confirmation code.")
        return data


class UpgradeForm(forms.Form):
    """ Subscription plan upgrade form """
    card_number = forms.CharField(required=False, max_length=20)
    card_holder = forms.CharField(required=False, max_length=50)
    card_expires_month = forms.ChoiceField(required=False,
        choices=[(n, '%02d' % n) for n in xrange(1, 13)])
    card_expires_year = forms.ChoiceField(required=False,
        choices=[(n, n) for n in xrange(2010, 2020)])
    card_cvv = forms.IntegerField(required=False)
    billing_zip_code = USZipCodeField(required=False)

    def __init__(self, free, **kwargs):
        super(UpgradeForm, self).__init__(**kwargs)
        self.free = free

    def clean_card_number(self):
        v = self.cleaned_data['card_number']
        if not self.free and not re.match(r'^(\d{4}\s?){4}$', v):
            raise forms.ValidationError("Oops! Your credit card number doesn't seem valid. Please review our credit card options.")
        return v

    def clean_card_holder(self):
        v = self.cleaned_data['card_holder']
        if not self.free and not re.match(r'^\s*\S+\s\S+', v):
            raise forms.ValidationError("You must enter the name as it appears on the credit card.")
        return v

    def subscribe(self, user, plan):
        """ Update remote Customer instance """
        authorize_gateway()
        customer = Customer.get(user.id)
        sub = customer.subscription
        sub.plan = Plan.get(plan.code)
        if not self.free:
            update_subscription(sub, self.cleaned_data, user)
        sub.save()


def authorize_gateway():
    """ Initialize CheddarGetter """
    CG.auth(settings.CHEDDAR_GETTER_USER, settings.CHEDDAR_GETTER_PASS)
    CG.set_product_code(settings.CHEDDAR_GETTER_PRODUCT)


def update_subscription(sub, data, user):
    """ Update credit card information """
    first_name, last_name = data['card_holder'].split(' ', 1)
    sub.cc_number = data['card_number'].replace(' ', '')
    sub.cc_first_name = first_name
    sub.cc_last_name = last_name
    sub.cc_expiration = '%02d/%s' % \
        (int(data['card_expires_month']), data['card_expires_year'])
    sub.cc_zip = data['billing_zip_code']
    sub.cc_card_code = '%03d' % data['card_cvv']
    if user.first_name != first_name or user.last_name != last_name:
        user.first_name = first_name
        user.last_name = last_name
        user.save()
