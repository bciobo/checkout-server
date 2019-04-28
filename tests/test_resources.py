# -*- coding: utf-8 -*-

"""
checkout-server.test_resources
~~~~~~~~~~~~

"""
import unittest
from unittest.mock import patch, MagicMock
from flask.testing import FlaskClient
# from checkout_server import make_app
from checkout_server import app, services, models


class TestConfig:
    """Flask app config used for testing."""

    TESTING = True


class CouponResourceTestCase(unittest.TestCase):
    endpoint = '/validate-coupon/'

    @patch('checkout_server.app.CouponCMS', spec=services.CouponCMS)
    def setUp(self, CouponCMSMock):
        self.coupon_cms_mock = CouponCMSMock.return_value
        self.api = app.make_app(TestConfig)
        self.client = FlaskClient(self.api, response_wrapper=self.api.response_class)

    def test_post_missing_code(self):
        rsp = self.client.post(self.endpoint, json={'price': 150.00},
                               content_type='application/json')
        self.assertEqual(rsp.status_code, 400)

    def test_post_missing_price(self):
        rsp = self.client.post(self.endpoint, json={'code': 'TESTING50%'},
                               content_type='application/json')
        self.assertEqual(rsp.status_code, 400)

    def test_post_coupon_not_found(self):
        self.coupon_cms_mock.get_coupon_by_code.return_value = None

        rsp = self.client.post(self.endpoint, json={'code': 'TESTING50%', 'price': 150.00},
                               content_type='application/json')
        self.assertEqual(rsp.status_code, 404)

    def test_post_calculate_price_invalid(self):
        coupon = models.Coupon('coupon_id', 'coll_id', 'TESTING50', 'my coupon', 'df', True, 50, 100, 500,
                               '2018-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z',
                               '2018-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z')

        self.coupon_cms_mock.get_coupon_by_code.return_value = coupon

        rsp = self.client.post(self.endpoint, json={'code': 'TESTING50%', 'price': -15},
                               content_type='application/json')
        self.assertEqual(rsp.status_code, 400)

    def test_post_calculate_coupon_invalid_exhausted(self):
        coupon = models.Coupon('coupon_id', 'coll_id', 'TESTING50', 'my coupon', 'df', True, 50, 100, 100,
                               '2019-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z',
                               '2018-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z')

        self.coupon_cms_mock.get_coupon_by_code.return_value = coupon

        rsp = self.client.post(self.endpoint, json={'code': 'TESTING50%', 'price': 150.00},
                               content_type='application/json')
        self.assertEqual(rsp.status_code, 403)

    def test_post_calculate_coupon_invalid_expired(self):
        coupon = models.Coupon('coupon_id', 'coll_id', 'TESTING50', 'my coupon', 'df', True, 50, 100, 200,
                               '2018-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z',
                               '2018-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z')

        self.coupon_cms_mock.get_coupon_by_code.return_value = coupon

        rsp = self.client.post(self.endpoint, json={'code': 'TESTING50%', 'price': 150.00},
                               content_type='application/json')
        self.assertEqual(rsp.status_code, 403)

    def test_post_calculate_price(self):
        coupon = models.Coupon('coupon_id', 'coll_id', 'TESTING50', 'my coupon', 'df', True, 50, 100, 200,
                               '2019-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z',
                               '2018-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z')

        self.coupon_cms_mock.get_coupon_by_code.return_value = coupon

        rsp = self.client.post(self.endpoint, json={'code': 'TESTING50%', 'price': 150.00},
                               content_type='application/json')
        self.assertEqual(rsp.status_code, 200)
        self.assertDictEqual(rsp.json, {'discount': 75.0, 'new_price': 75.0})
