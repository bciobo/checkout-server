# -*- coding: utf-8 -*-

"""
checkout-server.resources
~~~~~~~~~~~~

"""
import logging
from flask.views import MethodView
from flask import current_app, jsonify, abort

logger = logging.getLogger(__name__)


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
            return jsonify(self.stripe.Product.list(active=True))
        else:
            # return product with passed ID
            try:
                product = self.stripe.Product.retrieve(id=product_id)
                return jsonify(product)
            except Exception as e:
                logger.error(e)
                abort(404, 'Doodance: product ID is unknown')


class OrdersResource(CheckoutView):
    def get(self, order_id):
        try:
            return jsonify(self.stripe.Order.retrieve(order_id))
        except Exception as e:
            logger.error(e)
            abort(404, 'Doodance: order ID is unknown')

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
