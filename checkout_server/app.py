# -*- coding: utf-8 -*-

"""
checkout-server.app
~~~~~~~~~~~~

"""

from flask import Flask, redirect


def make_app(settings_override=None):
    """Create and configure the Flask app.
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('checkout_server.settings')
    app.config.from_pyfile('application.cfg', silent=True)
    app.config.from_object(settings_override)

    @app.route('/')
    def home():
        return redirect('hello')

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
