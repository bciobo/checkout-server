# -*- coding: utf-8 -*-

"""
checkout-server.resources
~~~~~~~~~~~~

"""
from flask.views import MethodView
from flask import current_app, jsonify


class CheckoutView(MethodView):

    def __init__(self, stripe):
        self.stripe = stripe


class ConfigResource(MethodView):
    def get(self):
        config = {'country': current_app.config.get('CHECKOUT_COUNTRY', 'DE'),
                  'currency': current_app.config.get('CHECKOUT_CURRENCY', 'eur'),
                  'stripePublishableKey': current_app.config.get('PUBLISHABLE_KEY', '')}
        return jsonify(config)


class ProductsResource(CheckoutView):
    def get(self, product_id):
        if not product_id:
            # return all available products
            return 'PRODUCT LIST'
        else:
            # return product with passed ID
            return 'PRODUCT ' + str(product_id)


class OrdersResource(CheckoutView):
    def get(self, order_id):
        if not order_id:
            # return 404
            return 'ORDER LIST'
        else:
            # return order with passed ID
            return 'ORDER ' + str(order_id)

    def post(self):
        # create new order
        print('creating a new order...')
        pass

    def patch(self):
        # update order metadata
        print('updating an order...')
        pass


class PayOrdersResource(CheckoutView):
    def post(self):
        print('paying an order...')


class Webhook(CheckoutView):
    def post(self):
        print('handling STRIPE event...')
