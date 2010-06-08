from django import forms
from django.contrib.auth.forms import UserCreationForm
#from django.utils.dates import MONTHS


class RegistrationForm(UserCreationForm):
    """ Registration processing """
    email = forms.EmailField(required=False)
    card_number = forms.CharField(required=False, max_length=20)
    card_holder = forms.CharField(required=False, max_length=50)
    card_expires_month = forms.ChoiceField(required=False,
        choices=[(n, '%02d' % n) for n in xrange(1, 13)])
    card_expires_year = forms.ChoiceField(required=False,
        choices=[(n, n) for n in xrange(2010, 2020)])

    def __init__(self, free, **kwargs):
        super(RegistrationForm, self).__init__(**kwargs)
        self.free = free
