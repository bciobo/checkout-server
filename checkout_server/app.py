# -*- coding: utf-8 -*-

"""
checkout-server.app
~~~~~~~~~~~~

"""

from flask import Flask
from . import resources


def make_app(settings_override=None):
    """Create and configure the Flask app.
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('checkout_server.settings')
    app.config.from_pyfile('application.cfg', silent=True)
    app.config.from_object(settings_override)

    # init and hook resources
    products_resource = resources.ProductsResource.as_view('products_api')
    orders_resource = resources.OrdersResource.as_view('orders_api')
    pay_orders_resource = resources.PayOrdersResource.as_view('pay_orders_api')
    webhook_resource = resources.Webhook.as_view('webhook')
    # products
    app.add_url_rule('/products/', defaults={'product_id': None},
                     view_func=products_resource, methods=['GET', ])
    app.add_url_rule('/products/<product_id>',
                     view_func=products_resource, methods=['GET', ])
    # orders
    app.add_url_rule('/orders/', defaults={'order_id': None},
                     view_func=orders_resource, methods=['POST', ])
    app.add_url_rule('/orders/<order_id>',
                     view_func=orders_resource, methods=['GET', 'PATCH'])
    app.add_url_rule('/orders/<order_id>/pay',
                     view_func=pay_orders_resource, methods=['POST', ])
    # webhook
    app.add_url_rule('/webhook/',
                     view_func=webhook_resource, methods=['POST', ])

    return app
