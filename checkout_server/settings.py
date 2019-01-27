# -*- coding: utf-8 -*-

"""
checkout-server.settings
~~~~~~~~~~~~

"""
import os

# Stripe
COUNTRY = 'DE'
API_VERSION = '2018-02-28'
PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Checkout form
CHECKOUT_COUNTRY = 'DE'
CHECKOUT_CURRENCY = 'eur'
