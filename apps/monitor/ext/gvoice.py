import csv
import sys
import re
import urllib
import urllib2

from django.conf import settings


class GoogleVoice(object):
    """Abstraction for interacting with Google Voice."""
    login_page_url = 'https://www.google.com/accounts/ServiceLogin'
    authenticate_url = 'https://www.google.com/accounts/ServiceLoginAuth'
    gv_home_page_url = 'https://www.google.com/voice/#inbox'
    email  = settings.GOOGLE_VOICE_USER
    passwd = settings.GOOGLE_VOICE_PASS

    def __init__(self):
        self._opener = None
        self._key = None

    @property
    def key(self):
        if not self._key:
            tmp = self.opener
        return self._key

    def open(self, *args, **kwargs):
        try:
            return self.opener.open(*args, **kwargs)
        except:
            if "attempts" in kwargs and not kwargs["attempts"]:
                raise
            kwargs["attempts"] -= 1
            self._opener = None
            return self.open(*args, **kwargs)

    @property
    def opener(self):
        if self._opener:
            return self._opener
        # TODO: auth stuff
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(self.opener)

        # Load sign in page
        login_page_contents = self.opener.open(self.login_page_url).read()

        # Find GALX value
        galx_match_obj = re.search(
          r'name="GALX"\s*value="([^"]+)"', login_page_contents, re.IGNORECASE)
        galx_value = \
          galx_match_obj.group(1) if galx_match_obj.group(1) is not None else ''

        # Set up login credentials
        login_params = urllib.urlencode({
            'Email' : self.email,
            'Passwd' : self.password,
            'continue' : 'https://www.google.com/voice/account/signin',
            'GALX': galx_value
        })
        # Login
        self.opener.open(self.authenticate_url, login_params)

        # Open GV home page
        gv_home_page_contents = self.opener.open(self.gv_home_page_url).read()

        # Fine _rnr_se value
        key = re.search('name="_rnr_se".*?value="(.*?)"', gv_home_page_contents)

        if not key:
            self.logged_in = False
        else:
            self.logged_in = True
            self.key = key.group(1)

class ContactLoader(object):
    contacts_csv_url = ("http://mail.google.com/mail/contacts/data/export?"
                        + "groupToExport=^Mine&exportType=ALL&out=OUTLOOK_CSV")

    def __init__(self):
      # Load ALL Google Contacts into csv dictionary
      self.contacts = csv.DictReader(gvoice.open(self.contacts_csv_url))

      # Create dictionary to store contacts and groups in an easier format
      self.contact_group = {}
      # Assigned each person to a group that we can get at later
      for row in self.contacts:
          if row['First Name'] != '':
              for category in row['Categories'].split(';'):
                  if category == '':
                      category  = 'Ungrouped'
                  if category not in self.contact_group:
                      self.contact_group[category] = [Contact(row)]
                  else:
                      self.contact_group[category].append(Contact(row))

      # Load contacts into a list of tuples...
      # [(1, ('group_name', [contact_list])),
      #  (2, ('group_name', [contact_list]))]
      items = self.contact_group.items()
      self.contacts_by_group_list = \
                [(id  + 1, group_contact_item)
                     for id, group_contact_item in enumerate(items)]

class Contact():
  def __init__(self, contact_detail):
      self.first_name = contact_detail['First Name'].strip()
      self.last_name = contact_detail['Last Name'].strip()
      self.mobile = contact_detail['Mobile Phone'].strip()
      self.email = contact_detail['E-mail Address'].strip()

  def __str__(self):
      return self.first_name + ' ' + self.last_name

# Class to assist in selected contacts by groups
class ContactSelector():
  def __init__(self, contacts_by_group_list):
      self.contacts_by_group_list = contacts_by_group_list
      self.contact_list = None

  def get_group_list(self):
      return [(item[0], item[1][0]) for item in self.contacts_by_group_list]

  def set_selected_group(self, group_id):
      self.contact_list  = self.contacts_by_group_list[group_id - 1][1][1]

  # Return the contact list so far
  def get_contacts_list(self):
      return [(id + 1, contact) for id, contact in enumerate(self.contact_list)]

  # Accept a list of indexes to remove from the current contact list
  # Assumes 1 based list being passed in
  def remove_from_contact_list(self, contacts_to_remove_list):
      if self.contact_list == None:
          return
      for id in contacts_to_remove_list:
          if id in range(0, len(self.contact_list)+1):
              self.contact_list[id - 1] = None
      self.contact_list = [contact for contact in self.contact_list if contact is not None]

class NumberRetriever():
  def __init__(self):
      self.phone_numbers_url = 'https://www.google.com/voice/settings/tab/phones'
      phone_numbers_page_content = gvoice.open(self.phone_numbers_url).read()

      # Build list of all numbers and their aliases
      self.phone_number_items = [(match.group(1), match.group(2))
                                 for match
                                 in re.finditer('"name":"([^"]+)","phoneNumber":"([^"]+)"',
                                                          phone_numbers_page_content)]

  def get_phone_numbers(self):
      return [(id + 1, (phone_number_item))
                for id, phone_number_item in enumerate(self.phone_number_items)]

class TextSender():
  sms_url = 'https://www.google.com/voice/sms/send/'
  def __init__(self):

      self.text = ''

  def send_text(self, phone_number):
      sms_params = urllib.urlencode({
          '_rnr_se': gvoice.key,
          'phoneNumber': phone_number,
          'text': self.text
      })
      # Send the text, display status message
      self.response  = gvoice.open(self.sms_url, sms_params).read()

class NumberDialer():
  call_url = 'https://www.google.com/voice/call/connect/'

  def __init__(self):
      self.forwarding_number = None

  def place_call(self, number):
      call_params = urllib.urlencode({
          'outgoingNumber' : number,
          'forwarding_number' : self.forwarding_number,
          'subscriberNumber' : 'undefined',
          'remember' : '0',
          '_rnr_se': gvoice.key
          })

      # Send the text, display status message
      self.response  = gvoice.open(self.call_url, call_params).read()

gvoice = GoogleVoice()

