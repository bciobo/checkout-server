# -*- coding: utf-8 -*-

"""
checkout-server.test_resources
~~~~~~~~~~~~

"""
import unittest
from copy import copy
from unittest.mock import patch, MagicMock
from flask.testing import FlaskClient
from checkout_server import app, services, models
from tests import mock_data


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

    def test_post_calculate_price_percentage(self):
        coupon = models.Coupon('coupon_id', 'coll_id', 'TESTING50', 'my coupon', 'df', True, 50, 100, 200,
                               '2019-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z',
                               '2018-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z')

        self.coupon_cms_mock.get_coupon_by_code.return_value = coupon

        rsp = self.client.post(self.endpoint, json={'code': 'TESTING50%', 'price': 150.00},
                               content_type='application/json')
        self.assertEqual(rsp.status_code, 200)
        self.assertDictEqual(rsp.json, {'discount': 75.0, 'new_price': 75.0})

    def test_post_calculate_price_absolute(self):
        coupon = models.Coupon('coupon_id', 'coll_id', 'TESTING50', 'my coupon', 'df', False, 50, 100, 200,
                               '2019-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z',
                               '2018-12-19T09:26:03.478039Z', '2018-12-19T09:26:03.478039Z')

        self.coupon_cms_mock.get_coupon_by_code.return_value = coupon

        rsp = self.client.post(self.endpoint, json={'code': 'TESTING50%', 'price': 150.00},
                               content_type='application/json')
        self.assertEqual(rsp.status_code, 200)
        self.assertDictEqual(rsp.json, {'discount': 50.0, 'new_price': 100.0})


class PayOrdersResourceTestCase(unittest.TestCase):
    order_id = mock_data.ORDER_CREATED['id']
    endpoint = '/orders/{order_id}/pay'

    @patch('checkout_server.app.stripe')
    def setUp(self, stripeMock):
        self.stripe_mock = stripeMock
        self.api = app.make_app(TestConfig)
        self.client = FlaskClient(self.api, response_wrapper=self.api.response_class)

    def test_post_missing_order_id_returns_405(self):
        rsp = self.client.post(self.endpoint.format(order_id=''), json={'source': None, 'coupon_code': None,
                                                                        'new_price': None})
        self.assertEqual(rsp.status_code, 405)

    def test_post_order_status_paid_returns_403(self):
        mock_order = copy(mock_data.ORDER_CREATED)
        mock_order.update({"status": "paid"})

        self.stripe_mock.Order.retrieve.return_value = mock_order

        rsp = self.client.post(self.endpoint.format(order_id=self.order_id),
                               json={'source': None, 'coupon_code': None, 'new_price': None})

        self.assertEqual(rsp.status_code, 403)

    def test_post_order_status_pending_returns_403(self):
        mock_order = copy(mock_data.ORDER_CREATED)
        mock_order.update({"status": "pending"})

        self.stripe_mock.Order.retrieve.return_value = mock_order

        rsp = self.client.post(self.endpoint.format(order_id=self.order_id),
                               json={'source': None, 'coupon_code': None, 'new_price': None})

        self.assertEqual(rsp.status_code, 403)

    @patch('checkout_server.resources.dynamic_3ds')
    def test_post_pay_is_called_for_card_source(self, dynamic_3ds_mock):
        # prep data
        mock_source = copy(mock_data.SOURCE_VISA)
        mock_order = copy(mock_data.ORDER_CREATED)
        pay_mock = MagicMock()
        setattr(mock_order, 'pay', pay_mock)
        # prep returns
        dynamic_3ds_mock.return_value = mock_source
        self.stripe_mock.Order.retrieve.return_value = mock_order
        # make the call
        rsp = self.client.post(self.endpoint.format(order_id=self.order_id),
                               json={'source': mock_source, 'coupon_code': None, 'new_price': None})
        # assert
        dynamic_3ds_mock.assert_called_once_with(self.stripe_mock, mock_source, mock_order)
        pay_mock.assert_called_with(source=mock_source['id'])
        self.assertEqual(rsp.status_code, 200)

    @patch('checkout_server.resources.dynamic_3ds')
    def test_post_charge_is_used_for_coupon_flow(self, dynamic_3ds_mock):
        # prep data
        mock_charge = copy(mock_data.CHARGE)
        create_charge_mock = MagicMock()
        mock_source = copy(mock_data.SOURCE_VISA)
        mock_order = copy(mock_data.ORDER_CREATED)
        order_modify_mock = MagicMock()
        dynamic_3ds_mock.return_value = mock_source
        self.stripe_mock.Order.retrieve.return_value = mock_order
        self.stripe_mock.Order.modify = order_modify_mock
        create_charge_mock.return_value = mock_charge
        self.stripe_mock.Charge.create = create_charge_mock
        # make the call
        rsp = self.client.post(self.endpoint.format(order_id=self.order_id),
                               json={'source': mock_source, 'coupon_code': 'TESTING50', 'new_price': 3000})
        # assert
        dynamic_3ds_mock.assert_called_once_with(self.stripe_mock, mock_source, mock_order)
        create_charge_mock.assert_called_once_with(amount=3000,
                                                   currency='eur',
                                                   metadata={'order_id': self.order_id,
                                                             'customer': "bogdan",
                                                             'coupon_code': 'TESTING50'})
        order_modify_mock.assert_called_once_with(self.order_id, metadata={'charge_id': mock_charge['id'],
                                                                           'coupon_code': 'TESTING50',
                                                                           'status': 'paid'})
        self.assertEqual(rsp.status_code, 200)
