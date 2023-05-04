import json
import os
import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_majordomo.settings')
# django.setup()

from finance_majordomo.users.models import User, get_default_display_options


def set_fields_to_user(user):

    json_fields = json.dumps(get_default_display_options())
    user.fields_to_display = json_fields
    user.save()


def set_fields_to_all_users():

    json_fields = json.dumps(get_default_display_options())

    for user in User.objects.all():
        user.fields_to_display = json_fields
        print(user.fields_to_display)
        user.save()


#set_fields_to_all_users()



