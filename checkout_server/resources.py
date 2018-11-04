# -*- coding: utf-8 -*-

"""
checkout-server.resources
~~~~~~~~~~~~

"""
from stripe.error import InvalidRequestError
from flask.views import MethodView
from flask import current_app as app, jsonify, abort



class CheckoutView(MethodView):

    def __init__(self, stripe):
        self.stripe = stripe


class ConfigResource(MethodView):
    def get(self):
        config = {'country': app.config.get('CHECKOUT_COUNTRY', 'DE'),
                  'currency': app.config.get('CHECKOUT_CURRENCY', 'eur'),
                  'stripePublishableKey': app.config.get('PUBLISHABLE_KEY', '')}
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
            except InvalidRequestError as invalid_req_err:
                app.logger.error(invalid_req_err.json_body.get('error'))
            except Exception as e:
                app.logger.error(e)
            finally:
                abort(404, 'Doodance: product ID is unknown')


class OrdersResource(CheckoutView):
    def get(self, order_id):
        try:
            return jsonify(self.stripe.Order.retrieve(order_id))
        except InvalidRequestError as invalid_req_err:
            app.logger.error(invalid_req_err.json_body.get('error'))
        except Exception as e:
            app.logger.error(e)
        finally:
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
