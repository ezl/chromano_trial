import re

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.localflavor.us.forms import USPhoneNumberField
#from django.utils.dates import MONTHS

from models import UserProfile


class RegistrationForm(UserCreationForm):
    """ Registration processing """
    username = forms.EmailField(required=True)
    card_number = forms.CharField(required=False, max_length=20)
    card_holder = forms.CharField(required=False, max_length=50)
    card_expires_month = forms.ChoiceField(required=False,
        choices=[(n, '%02d' % n) for n in xrange(1, 13)])
    card_expires_year = forms.ChoiceField(required=False,
        choices=[(n, n) for n in xrange(2010, 2020)])

    def __init__(self, free, **kwargs):
        super(RegistrationForm, self).__init__(**kwargs)
        self.free = free

    def clean_card_number(self):
        v = self.cleaned_data['card_number']
        if not self.free and not re.match(r'^(\d{4}\s?){4}$', v):
            raise forms.ValidationError("Card number is incorrect")
        return v

    def clean_card_holder(self):
        v = self.cleaned_data['card_holder']
        if not self.free and not re.match(r'^\s*\S+\s\S+', v):
            raise forms.ValidationError("Enter cardholder name")
        return v


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
            raise forms.ValidationError("Confirmation string is incorrect")
        return data


class UpgradeForm(forms.Form):
    """ Subscription plan upgrade form """
    card_number = forms.CharField(required=False, max_length=20)
    card_holder = forms.CharField(required=False, max_length=50)
    card_expires_month = forms.ChoiceField(required=False,
        choices=[(n, '%02d' % n) for n in xrange(1, 13)])
    card_expires_year = forms.ChoiceField(required=False,
        choices=[(n, n) for n in xrange(2010, 2020)])

    def __init__(self, free, **kwargs):
        super(UpgradeForm, self).__init__(**kwargs)
        self.free = free

    def clean_card_number(self):
        v = self.cleaned_data['card_number']
        if not self.free and not re.match(r'^(\d{4}\s?){4}$', v):
            raise forms.ValidationError("Card number is incorrect")
        return v

    def clean_card_holder(self):
        v = self.cleaned_data['card_holder']
        if not self.free and not re.match(r'^\s*\S+\s\S+', v):
            raise forms.ValidationError("Enter cardholder name")
        return v
    