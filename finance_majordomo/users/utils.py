import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_majordomo.settings')
django.setup()

from finance_majordomo.users.models import User

fields = {'ticker': True,
          'name': True,
          'currency': True,
          'quantity': True,
          'purchase_price': True,
          'current_price': True,
          'dividends_recieved': True,
          'percent_result': True,
          }

def set_fields_to_user(user):

    json_fields = json.dumps(fields)
    user.fields_to_display = json_fields
    user.save()


def set_fields_to_all_users():

    json_fields = json.dumps(fields)

    for user in User.objects.all():
        user.fields_to_display = json_fields
        print(user.fields_to_display)
        user.save()


#set_fields_to_all_users()



