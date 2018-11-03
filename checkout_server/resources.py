# -*- coding: utf-8 -*-

"""
checkout-server.resources
~~~~~~~~~~~~

"""
from flask.views import MethodView


class ProductsResource(MethodView):
    def get(self, product_id):
        if not product_id:
            # return all available products
            return 'PRODUCT LIST'
        else:
            # return product with passed ID
            return 'PRODUCT ' + str(product_id)


class OrdersResource(MethodView):
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


class PayOrdersResource(MethodView):
    def post(self):
        print('paying an order...')


class Webhook(MethodView):
    def post(self):
        print('handling STRIPE event...')
