# -*- coding: utf-8 -*-

"""
checkout-server.models
~~~~~~~~~~~~

"""
from datetime import datetime

import attr
from attr import validators

datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"


class InvalidCouponError(Exception):
    pass


class InvalidAmountError(Exception):
    pass


@attr.s
class Coupon:
    id = attr.ib(validator=validators.instance_of(str))
    collection_id = attr.ib(validator=validators.instance_of(str))
    code = attr.ib(validator=validators.instance_of(str))
    name = attr.ib(validator=validators.instance_of(str))
    kurs = attr.ib(validator=[validators.instance_of(str), ])  # validators.in_(['df', 'DF', 'lw', 'LW', 'ww', 'WW'])])
    prozent = attr.ib(validator=validators.instance_of(bool))
    rabat_hohe = attr.ib(converter=(lambda x: float(x)), validator=validators.instance_of(float))
    eingelost = attr.ib(validator=validators.instance_of(int))
    erstellt = attr.ib(validator=validators.instance_of(int))
    gultig_bis = attr.ib(converter=(lambda d: datetime.strptime(d, datetime_format)),
                         validator=validators.instance_of(datetime))
    updated_on = attr.ib(converter=(lambda d: datetime.strptime(d, datetime_format)),
                         validator=validators.instance_of(datetime))
    created_on = attr.ib(converter=(lambda d: datetime.strptime(d, datetime_format)),
                         validator=validators.instance_of(datetime))
    published_on = attr.ib(converter=(lambda d: datetime.strptime(d, datetime_format)),
                           validator=validators.instance_of(datetime))

    @staticmethod
    def _map_data_to_model(data):
        return Coupon(data['_id'], data['_cid'], data['code'], data['name'], data['kurs'], data['prozent'],
                      data['rabat-hohe'], data['eingelost'], data['erstellt'], data['gultig-bis'], data['updated-on'],
                      data['created-on'], data['published-on'])

    @property
    def is_expired(self):
        return bool(self.gultig_bis < datetime.utcnow())

    @property
    def is_exhausted(self):
        return bool(self.erstellt - self.eingelost <= 0)

    @property
    def is_valid(self):
        return not self.is_expired and not self.is_exhausted

    def apply(self, price):
        if price < 0.0:
            raise InvalidAmountError('Price must be greater than 0')

        if not self.is_valid:
            raise InvalidCouponError

        reduced_price = (price - (price * self.rabat_hohe / 100)) if self.prozent else (price - self.rabat_hohe)

        return reduced_price if reduced_price >= 0 else price
