import json

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_majordomo.settings')
# django.setup()
from .fields_to_display import get_default_display_options
from finance_majordomo.users.models import User


def set_fields_to_user(user, display_options_dict=None):

    if display_options_dict is None:
        display_options_dict = get_default_display_options()

    json_display_options = json.dumps(display_options_dict)
    user.fields_to_display = json_display_options
    user.save()


def set_fields_to_all_users():

    json_fields = json.dumps(get_default_display_options())

    for user in User.objects.all():
        user.fields_to_display = json_fields
        print(user.fields_to_display)
        user.save()


#set_fields_to_all_users()



