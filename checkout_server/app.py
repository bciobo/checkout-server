# -*- coding: utf-8 -*-

"""
checkout-server.app
~~~~~~~~~~~~

"""
import logging
from . import resources
import stripe
from flask import Flask, request
from flask.logging import default_handler
from flask_cors import CORS


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url
        record.remote_addr = request.remote_addr
        return super().format(record)


def make_app(settings_override=None):
    """Create and configure the Flask app.
    """
    app = Flask(__name__, instance_relative_config=True, static_url_path='')

    app.config.from_object('checkout_server.settings')
    app.config.from_pyfile('application.cfg', silent=True)
    app.config.from_object(settings_override)
    # logging formatter for requests
    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )
    default_handler.setFormatter(formatter)

    # Stripe
    stripe.api_key = app.config['SECRET_KEY']
    stripe.api_version = app.config.get('API_VERSION')
    stripe.default_http_client = stripe.http_client.RequestsClient()

    # init and hook resources
    config_resource = resources.ConfigResource.as_view('config_api')
    products_resource = resources.ProductsResource.as_view('products_api', stripe)
    orders_resource = resources.OrdersResource.as_view('orders_api', stripe)
    pay_orders_resource = resources.PayOrdersResource.as_view('pay_orders_api', stripe)
    webhook_resource = resources.Webhook.as_view('webhook', stripe)
    static_resource = resources.Bundle.as_view('bundle')

    # config
    app.add_url_rule('/config/',
                     view_func=config_resource, methods=['GET', ])
    # products
    app.add_url_rule('/products/', defaults={'product_id': None},
                     view_func=products_resource, methods=['GET', ])
    app.add_url_rule('/products/<product_id>',
                     view_func=products_resource, methods=['GET', ])
    # orders
    app.add_url_rule('/orders/',
                     view_func=orders_resource, methods=['POST', ])
    app.add_url_rule('/orders/<order_id>', defaults={'order_id': None},
                     view_func=orders_resource, methods=['GET', ])
    app.add_url_rule('/orders/<order_id>/pay',
                     view_func=pay_orders_resource, methods=['POST', ])
    # webhook
    app.add_url_rule('/webhook/',
                     view_func=webhook_resource, methods=['POST', ])
    # static files
    app.add_url_rule('/bundle/<path:filename>',
                     view_func=static_resource, methods=['GET', ])

    CORS(app)
    return app
