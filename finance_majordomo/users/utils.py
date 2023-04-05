import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_majordomo.settings')
django.setup()

from finance_majordomo.users.models import User


def set_fields():
    fields = {'Ticker': 1,
              'Name': 1,
              'Currency': 1,
              'Quantity': 1,
              'Purchase price': 1,
              'Current price': 1,
              'Result': 1
              }
    json_fields = json.dumps(fields)
    print(json_fields)
    for user in User.objects.all():
        user.fields_to_display = json_fields
        print(user.fields_to_display)
        user.save()



