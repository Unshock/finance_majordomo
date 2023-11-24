from django.test import TestCase



class BaseTest(TestCase):

    fixtures = [
        'user.json',
        'AssetsHistoricalData.json',
        'assets.json',

    ]



