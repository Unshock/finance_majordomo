import json
import simplejson
from service_objects.fields import ModelField
from service_objects.services import Service
from django import forms

from common.utils.stocks import get_asset_description, get_bond_coupon_history
from finance_majordomo.stocks.services.accrual_services.dividend_model_management_services import \
    execute_accrual_model_data_filling_service
from finance_majordomo.stocks.services.accrual_services.dividends_parser_services import \
    get_share_dividends

from finance_majordomo.stocks.models.asset import Asset, Bond, Stock
from finance_majordomo.stocks.utils.assets_utils import get_asset_history_data,\
    add_share_history_data_to_model2, add_bond_history_data_to_model2


def get_or_create_asset_obj(
        asset_sec_id: str, primary_board_id: str = None) -> Asset:
    """
    :param asset_sec_id: asset security id
    :param primary_board_id: primary_board_id from asset data
    :return: either finds asset in Assets or gets the description and
        executes func that creates asset and returns asset object.
    """

    try:
        asset_obj = Asset.objects.get(secid=asset_sec_id)

    except Asset.DoesNotExist:
        print(f'Start creating asset - {asset_sec_id}')
        asset_description = get_asset_description(asset_sec_id)
        asset_description['primary_boardid'] = primary_board_id

        asset_obj = create_asset_obj_from_description(asset_description)

    return asset_obj


def create_asset_obj_from_description(asset_description: dict) -> Asset:
    """
    :param asset_description: asset description from apimoex
    :return: returns nothing but normalizes some fields and executes asset
        creation service
    """
    create_asset_service_kwargs = {
        'secid': asset_description.get('SECID'),
        'isin': asset_description.get('ISIN'),
        'name': asset_description.get('SHORTNAME'),
        'latname': asset_description.get('LATNAME'),

        'currency': 'RUR' if asset_description.get(
            'FACEUNIT') == 'SUR' else asset_description.get('FACEUNIT'),
        'issuedate': asset_description.get('ISSUEDATE'),
        'isqualifiedinvestors': True if asset_description.get(
            'ISQUALIFIEDINVESTORS') == '1' else False,
        'morningsession':
            True if asset_description.get('MORNINGSESSION') == '1' else False,
        'eveningsession':
            True if asset_description.get('EVENINGSESSION') == '1' else False,

        'type': asset_description.get('TYPE'),
        'typename': asset_description.get('TYPENAME'),

        'group': asset_description.get('GROUP'),
        'groupname': asset_description.get('GROUPNAME'),
        'primary_boardid': asset_description.get('primary_boardid'),

        'startdatemoex': asset_description.get('STARTDATEMOEX'),
        'buybackdate': asset_description.get('BUYBACKDATE'),
        'matdate': asset_description.get('MATDATE'),
        'couponfrequency': asset_description.get('COUPONFREQUENCY'),
        'couponpercent': asset_description.get('COUPONPERCENT'),
        'couponvalue': asset_description.get('COUPONVALUE'),
        'days_to_redemption': asset_description.get('DAYSTOREDEMPTION'),
        'face_value': asset_description.get('FACEVALUE')
    }

    return execute_create_asset_service(**create_asset_service_kwargs)


def execute_create_asset_service(
        *, secid=None, isin=None, name=None, latname=None, currency=None,
        issuedate=None, isqualifiedinvestors=None, morningsession=None,
        eveningsession=None, type=None, typename=None, group=None,
        groupname=None, primary_boardid=None, asset_type=None,
        startdatemoex=None, buybackdate=None, matdate=None,
        couponfrequency=None, couponpercent=None, couponvalue=None,
        days_to_redemption=None, face_value=None):
    """
     - Gets asset model parameters.
    :return: executes CreateAssetService and returns asset object created using
        provided parameters
    """

    return CreateAssetService.execute({
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
        'asset_type': group,  # mb to delete +++++++++++++++++++++++
        'startdatemoex': startdatemoex,
        'buybackdate': buybackdate,
        'matdate': matdate,
        'couponfrequency': couponfrequency,
        'couponpercent': couponpercent,
        'couponvalue': couponvalue,
        'days_to_redemption': days_to_redemption,
        'face_value': face_value,
    })


class CreateAssetService(Service):

    secid = forms.CharField()
    isin = forms.CharField()
    name = forms.CharField()
    latname = forms.CharField()

    currency = forms.CharField()
    issuedate = forms.DateField(required=False)

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
        self._fill_with_accrual_data(asset_obj)

        return asset_obj

    def _create_base_asset(self):

        asset_obj = Asset.objects.create(
            secid=self.cleaned_data.get('secid'),
            isin=self.cleaned_data.get('isin'),
            name=self.cleaned_data.get('name'),
            latname=self.cleaned_data.get('latname'),

            currency=self.cleaned_data.get('currency'),
            issuedate=self.cleaned_data.get('issuedate'),

            isqualifiedinvestors=self.cleaned_data.get('isqualifiedinvestors'),
            morningsession=self.cleaned_data.get('morningsession'),
            eveningsession=self.cleaned_data.get('eveningsession'),

            type=self.cleaned_data.get('type'),
            typename=self.cleaned_data.get('typename'),
            group=self.cleaned_data.get('group'),
            groupname=self.cleaned_data.get('groupname'),

            primary_boardid=self.cleaned_data.get('primary_boardid')
        )

        return asset_obj

    def _create_sub_asset(self, asset):
        if asset.group == 'stock_shares':
            execute_create_share_service(asset)

        elif asset.group == 'stock_bonds':

            create_bond_service_kwargs = {
                'startdatemoex': self.cleaned_data.get('startdatemoex'),
                'buybackdate': self.cleaned_data.get('buybackdate'),
                'matdate': self.cleaned_data.get('matdate'),
                'couponfrequency': self.cleaned_data.get('couponfrequency'),
                'couponpercent': self.cleaned_data.get('couponpercent'),
                'couponvalue': self.cleaned_data.get('couponvalue'),
                'days_to_redemption': self.cleaned_data.get(
                    'days_to_redemption'),
                'face_value': self.cleaned_data.get('face_value')
            }

            execute_create_bond_service(asset, **create_bond_service_kwargs)

        else:
            raise Exception(f'group is incorrect or unsupported: {asset.group}')

    def _fill_with_historical_data(self, asset_obj):
        historical_data = get_asset_history_data(asset_obj)

        if asset_obj.group == 'stock_shares':
            self._fill_share_with_historical_data(asset_obj, historical_data)

        elif asset_obj.group == 'stock_bonds':
            self._fill_bond_with_historical_data(asset_obj, historical_data)

        else:
            raise Exception(
                f'group is incorrect or unsupported: {asset_obj.group}'
            )

    @staticmethod
    def _fill_share_with_historical_data(asset_obj, historical_data):
        try:
            add_share_history_data_to_model2(asset_obj, historical_data)

        except Exception as e:
            print(e)
            pass

    @staticmethod
    def _fill_bond_with_historical_data(asset_obj, historical_data):
        try:
            add_bond_history_data_to_model2(asset_obj, historical_data)

        except Exception('HISTORY PROBLEM'):
            pass

    @staticmethod
    def _fill_with_accrual_data(asset_obj):

        if asset_obj.group == 'stock_shares':

            accrual_data_dict = get_share_dividends(asset_obj)
            execute_accrual_model_data_filling_service(
                asset=asset_obj, accrual_data_dict=accrual_data_dict)

        elif asset_obj.group == 'stock_bonds':

            accrual_data_dict = get_bond_coupon_history(asset_obj.secid)
            execute_accrual_model_data_filling_service(
                asset=asset_obj, accrual_data_dict=accrual_data_dict
            )

        else:
            raise Exception(f'unsupported group: {asset_obj.group}')


def execute_create_share_service(asset: Asset) -> Stock:
    """
     - Gets asset object and share unique parameters.
    :return: executes CreateShareService and returns share object created using
        provided parameters
    """
    return CreateShareService.execute({
        'asset': asset
    })


class CreateShareService(Service):
    asset = ModelField(Asset)

    def process(self):
        self.asset = self.cleaned_data.get('asset')
        return self._create_share_object()

    def _create_share_object(self):

        share_obj = Stock.objects.create(
            asset_ptr=self.asset,
            creation_date=self.asset.creation_date,
            isqualifiedinvestors=self.asset.isqualifiedinvestors,
            morningsession=self.asset.morningsession,
            eveningsession=self.asset.eveningsession,
        )
        return share_obj


def execute_create_bond_service(
        asset: Asset, *, startdatemoex=None, buybackdate=None, matdate=None,
        couponfrequency=None, couponpercent=None, couponvalue=None,
        days_to_redemption=None, face_value=None) -> Bond:
    """
     - Gets asset object and bond unique parameters.
    :return: executes CreateBondService and returns bond object created using
        provided parameters
    """
    return CreateBondService.execute({
        'asset': asset,
        'startdatemoex': startdatemoex,
        'buybackdate': buybackdate,
        'matdate': matdate,
        'couponfrequency': couponfrequency,
        'couponpercent': couponpercent,
        'couponvalue': couponvalue,
        'days_to_redemption': days_to_redemption,
        'face_value': face_value
    })


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
        self.asset = self.cleaned_data.get('asset')
        return self._create_bond_object()

    def _create_bond_object(self):

        startdatemoex = self.cleaned_data.get('startdatemoex')
        buybackdate = self.cleaned_data.get('buybackdate')
        matdate = self.cleaned_data.get('matdate')
        couponfrequency = self.cleaned_data.get('couponfrequency')
        couponpercent = self.cleaned_data.get('couponpercent')
        couponvalue = self.cleaned_data.get('couponvalue')
        days_to_redemption = self.cleaned_data.get('days_to_redemption')
        face_value = self.cleaned_data.get('face_value')

        bond_obj = Bond.objects.create(
            asset_ptr=self.asset,
            creation_date=self.asset.creation_date,
            isqualifiedinvestors=self.asset.isqualifiedinvestors,
            morningsession=self.asset.morningsession,
            eveningsession=self.asset.eveningsession,

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
