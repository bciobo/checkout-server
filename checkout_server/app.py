# -*- coding: utf-8 -*-

"""
checkout-server.app
~~~~~~~~~~~~

"""
from . import resources
import stripe
from flask import Flask


def make_app(settings_override=None):
    """Create and configure the Flask app.
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('checkout_server.settings')
    app.config.from_pyfile('application.cfg', silent=True)
    app.config.from_object(settings_override)

    # Stripe
    stripe.api_key = app.config['SECRET_KEY']
    stripe.set_app_info(name='Doodance checkout server', version=app.config.get('API_VERSION'))
    stripe.default_http_client = stripe.http_client.RequestsClient()

    # init and hook resources
    config_resource = resources.ConfigResource.as_view('config_api')
    products_resource = resources.ProductsResource.as_view('products_api', stripe)
    orders_resource = resources.OrdersResource.as_view('orders_api', stripe)
    pay_orders_resource = resources.PayOrdersResource.as_view('pay_orders_api', stripe)
    webhook_resource = resources.Webhook.as_view('webhook', stripe)
    # config
    app.add_url_rule('/config/',
                     view_func=config_resource, methods=['GET', ])
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
