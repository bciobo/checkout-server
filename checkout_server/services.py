# -*- coding: utf-8 -*-

"""
checkout-server.services
~~~~~~~~~~~~

"""
import requests
import logging

from checkout_server.models import Coupon

logger = logging.getLogger(__file__)


class CouponCMS:
    def __init__(self, api_token, collection_id):
        self.api_token = api_token
        self.collection_id = collection_id
        self.headers = {'Authorization': 'Bearer {}'.format(self.api_token), 'accept-version': '1.0.0'}

    def get_coupons(self):
        url = 'https://api.webflow.com/collections/{}/items'.format(self.collection_id)
        rsp = requests.get(url, headers=self.headers)
        if rsp.ok:
            data = rsp.json()
            return list(map(Coupon._map_data_to_model, data.get('items', [])))
        else:
            return []

    def get_coupon(self, coupon_id):
        url = 'https://api.webflow.com/collections/{}/items/{}'.format(self.collection_id, coupon_id)
        rsp = requests.get(url, headers=self.headers)
        if rsp.ok:
            data = rsp.json()
            coupon_dict = data.get('items')[0]  # TODO make it failsafe
            return Coupon._map_data_to_model(coupon_dict)

    def get_coupon_by_code(self, code):
        coupons = self.get_coupons()
        for coupon in coupons:
            if coupon.code == code:
                return coupon

    def update_coupon(self, coupon, updates):
        url = 'https://api.webflow.com/collections/{}/items/{}'.format(coupon.collection_id, coupon.id)
        rsp = requests.patch(url, params={'live': True}, json={'fields': updates}, headers=self.headers)
        return rsp.ok

    def use_once(self, coupon):
        return self.update_coupon(coupon, {'eingelost': coupon.eingelost + 1})
