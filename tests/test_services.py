# -*- coding: utf-8 -*-

"""
checkout-server.test_services
~~~~~~~~~~~~

"""
import pytest
import responses

from checkout_server.services import CouponCMS
from checkout_server.models import Coupon

test_coupon_dict = {'_archived': False,
                    '_draft': False,
                    'gultig-bis': '2019-12-07T00:00:00.000Z',
                    'prozent': True,
                    'rabat-hohe': 50,
                    'eingelost': 34,
                    'erstellt': 100,
                    'kurs': 'df',
                    'name': '50% Rabatt für Hans auf DF-Kurs',
                    'code': 'HansDF50%',
                    'slug': 'ipsum-dolores',
                    'updated-on': '2019-04-03T20:37:12.507Z',
                    'updated-by': 'Person_59bc3a41a1281d0001889570',
                    'created-on': '2019-04-03T20:30:56.173Z',
                    'created-by': 'Person_59bc3a41a1281d0001889570',
                    'published-on': '2019-04-09T14:41:51.132Z',
                    'published-by': 'Person_59bc3a41a1281d0001889570',
                    '_cid': '5ca517f85ad172401c8fd4ee',
                    '_id': '5ca518002ec41b3f6ef4229f'}


class TestWebflowCMS:
    pass
