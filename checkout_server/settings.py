# -*- coding: utf-8 -*-

"""
checkout-server.settings
~~~~~~~~~~~~

"""
import os

# Stripe
COUNTRY = 'DE'
API_VERSION = '2018-02-06'
PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY',
                            'pk_test_CiXf29IdSdWEmeZGORUfnSFc')
SECRET_KEY = os.getenv('STRIPE_SECRET_KEY',
                       'sk_test_qa9ceFzzUpWu3EvMHsoHs65d')
WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET',
                           'whsec_TUjpJ0NduzHQfHFciBPN5JcsmECA97Bj')

# Checkout form
CHECKOUT_COUNTRY = 'DE'
CHECKOUT_CURRENCY = 'eur'
