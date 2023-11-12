from service_objects.fields import ModelField
from service_objects.services import Service
from django import forms

from common.utils.stocks import get_asset_description, get_bond_coupon_history
from finance_majordomo.dividends.utils import get_stock_dividends, \
    add_dividends_to_model
from finance_majordomo.stocks.models import Asset, Bond, Stock
from finance_majordomo.stocks.utils import get_asset_history_data, \
    add_share_history_data_to_model2, add_bond_history_data_to_model2



def get_or_create_asset_obj(
        asset_secid: str, primary_boardid: str = None) -> Asset:

    print('[[[[[[[[[[[[[[[[[[[[[[', asset_secid)

    try:
        asset_obj = Asset.objects.get(secid=asset_secid)

    except Asset.DoesNotExist:
        asset_description = get_asset_description(asset_secid)
        asset_description['primary_boardid'] = primary_boardid
        asset_obj = create_asset_obj_from_description(asset_description)

    return asset_obj


def create_asset_obj_from_description(asset_description: dict) -> Asset:
    secid = asset_description.get('SECID')
    isin = asset_description.get('ISIN')

    name = asset_description.get('SHORTNAME')
    latname = asset_description.get('LATNAME')

    currency = 'RUR' if asset_description.get(
        'FACEUNIT') == 'SUR' else asset_description.get('FACEUNIT')
    issuedate = asset_description.get('ISSUEDATE')

    isqualifiedinvestors = True if \
        asset_description.get('ISQUALIFIEDINVESTORS') == '1' else False
    morningsession = True if \
        asset_description.get('MORNINGSESSION') == '1' else False
    eveningsession = True if \
        asset_description.get('EVENINGSESSION') == '1' else False

    type = asset_description.get('TYPE')
    typename = asset_description.get('TYPENAME')

    group = asset_description.get('GROUP')
    groupname = asset_description.get('GROUPNAME')
    primary_boardid = asset_description.get('primary_boardid')

    #asset_type = get_normalized_asset_type(type)

    startdatemoex = asset_description.get('STARTDATEMOEX')
    buybackdate = asset_description.get('BUYBACKDATE')
    matdate = asset_description.get('MATDATE')
    couponfrequency = asset_description.get('COUPONFREQUENCY')
    couponpercent = asset_description.get('COUPONPERCENT')
    couponvalue = asset_description.get('COUPONVALUE')
    days_to_redemption = asset_description.get('DAYSTOREDEMPTION')
    face_value = asset_description.get('FACEVALUE')

    asset = CreateAssetService.execute({
        'secid': secid,
        'isin': isin,
        'name': name,
        'latname': latname,
        'currency': currency,
        'issuedate': issuedate,
        'isqualifiedinvestors': isqualifiedinvestors,
        'morningsession': morningsession,
        'eveningsession': eveningsession,
        'type': type,
        'typename': typename,
        'group': group,
        'groupname': groupname,
        'primary_boardid': primary_boardid,
        'asset_type': group, # mb to delete
        'startdatemoex': startdatemoex,
        'buybackdate': buybackdate,
        'matdate': matdate,
        'couponfrequency': couponfrequency,
        'couponpercent': couponpercent,
        'couponvalue': couponvalue,
        'days_to_redemption': days_to_redemption,
        'face_value': face_value,
    })

    return asset


class CreateAssetService(Service):

    secid = forms.CharField()
    isin = forms.CharField()
    name = forms.CharField()
    latname = forms.CharField()

    currency = forms.CharField()
    issuedate = forms.DateField()

    isqualifiedinvestors = forms.BooleanField(required=False)
    morningsession = forms.BooleanField(required=False)
    eveningsession = forms.BooleanField(required=False)

    type = forms.CharField()
    typename = forms.CharField()

    group = forms.CharField()
    groupname = forms.CharField()
    primary_boardid = forms.CharField()

    startdatemoex = forms.DateField(required=False)
    buybackdate = forms.DateField(required=False)
    matdate = forms.DateField(required=False)
    couponfrequency = forms.IntegerField(required=False)
    couponpercent = forms.DecimalField(required=False)
    couponvalue = forms.DecimalField(required=False)
    days_to_redemption = forms.IntegerField(required=False)
    face_value = forms.DecimalField(required=False)

    def process(self):
        asset_obj = self._create_base_asset()
        self._create_sub_asset(asset_obj)
        self._fill_with_historical_data(asset_obj)
        self._fill_with_accrual(asset_obj)

        return asset_obj

    def _create_base_asset(self):
        secid = self.cleaned_data['secid']
        isin = self.cleaned_data['isin']
        name = self.cleaned_data['name']
        latname = self.cleaned_data['latname']

        currency = self.cleaned_data['currency']
        issuedate = self.cleaned_data['issuedate']

        isqualifiedinvestors = self.cleaned_data['isqualifiedinvestors']
        morningsession = self.cleaned_data['morningsession']
        eveningsession = self.cleaned_data['eveningsession']

        type = self.cleaned_data['type']
        typename = self.cleaned_data['typename']

        group = self.cleaned_data['group']
        groupname = self.cleaned_data['groupname']
        primary_boardid = self.cleaned_data['primary_boardid']

        user = self.cleaned_data.get('user')

        asset_obj = Asset.objects.create(
            secid=secid,
            isin=isin,
            name=name,
            latname=latname,
            currency=currency,
            issuedate=issuedate,
            isqualifiedinvestors=isqualifiedinvestors,
            morningsession=morningsession,
            eveningsession=eveningsession,
            type=type,
            typename=typename,
            group=group,
            groupname=groupname,
            primary_boardid=primary_boardid,
        )

        return asset_obj

    def _create_sub_asset(self, asset):
        if asset.group == 'stock_shares':
            CreateShareService.execute({
                'asset': asset,
            })

        elif asset.group == 'stock_bonds':

            startdatemoex = self.cleaned_data['startdatemoex']
            buybackdate = self.cleaned_data['buybackdate']
            matdate = self.cleaned_data['matdate']
            couponfrequency = self.cleaned_data['couponfrequency']
            couponpercent = self.cleaned_data['couponpercent']
            couponvalue = self.cleaned_data['couponvalue']
            days_to_redemption = self.cleaned_data['days_to_redemption']
            face_value = self.cleaned_data['face_value']

            CreateShareService.execute({
                'asset': asset,

                'startdatemoex': startdatemoex,
                'buybackdate': buybackdate,
                'matdate': matdate,
                'couponfrequency': couponfrequency,
                'couponpercent': couponpercent,
                'couponvalue': couponvalue,
                'days_to_redemption': days_to_redemption,
                'face_value': face_value,
            })

        else:
            raise Exception('type is incorrect')

    def _fill_with_historical_data(self, asset_obj):
        historical_data = get_asset_history_data(asset_obj)

        if asset_obj.group == 'stock_shares':
            self._fill_share_with_historical_data(asset_obj, historical_data)

        elif asset_obj.group == 'stock_bonds':
            self._fill_bond_with_historical_data(asset_obj, historical_data)

        else:
            raise Exception('type is incorrect')

    @staticmethod
    def _fill_share_with_historical_data(asset_obj, historical_data):
        try:
            add_share_history_data_to_model2(asset_obj, historical_data)

        except Exception as e:
            print('2', e)
            pass

    @staticmethod
    def _fill_bond_with_historical_data(asset_obj, historical_data):
        try:
            add_bond_history_data_to_model2(asset_obj, historical_data)

        except Exception('HISTORY PROBLEM'):
            pass

    @staticmethod
    def _fill_with_accrual(asset_obj):

        if asset_obj.group == 'stock_shares':
            accrual_dict = get_stock_dividends(asset_obj)
            add_dividends_to_model(asset_obj, accrual_dict)

        elif asset_obj.group == 'stock_bonds':
            accrual_dict = get_bond_coupon_history(asset_obj.secid)
            add_dividends_to_model(asset_obj, accrual_dict)

        else:
            pass


class CreateShareService(Service):
    asset = ModelField(Asset)

    def process(self):

        asset = self.cleaned_data['asset']

        print(asset.secid)
        print(asset.isqualifiedinvestors)

        share_obj = Stock.objects.create(
            asset_ptr=asset,
            creation_date=asset.creation_date,
            isqualifiedinvestors=asset.isqualifiedinvestors,
            morningsession=asset.morningsession,
            eveningsession=asset.eveningsession,
        )
        return share_obj


class CreateBondService(Service):

    startdatemoex = forms.DateField()
    buybackdate = forms.DateField(required=False)
    matdate = forms.DateField()
    couponfrequency = forms.IntegerField()
    couponpercent = forms.DecimalField(required=False)
    couponvalue = forms.DecimalField(required=False)
    days_to_redemption = forms.IntegerField(required=False)
    face_value = forms.DecimalField(required=False)

    asset = ModelField(Asset)

    def process(self):
        asset = self.cleaned_data['asset']

        startdatemoex = self.cleaned_data['startdatemoex']
        buybackdate = self.cleaned_data['buybackdate']
        matdate = self.cleaned_data['matdate']
        couponfrequency = self.cleaned_data['couponfrequency']
        couponpercent = self.cleaned_data['couponpercent']
        couponvalue = self.cleaned_data['couponvalue']
        days_to_redemption = self.cleaned_data['days_to_redemption']
        face_value = self.cleaned_data['face_value']

        bond_obj = Bond.objects.create(
            asset_ptr=asset,
            creation_date=asset.creation_date,

            startdatemoex=startdatemoex,
            buybackdate=buybackdate,
            matdate=matdate,
            couponfrequency=couponfrequency,
            couponpercent=couponpercent,
            couponvalue=couponvalue,
            days_to_redemption=days_to_redemption,
            face_value=face_value,
        )

        return bond_obj
