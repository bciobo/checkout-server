# -*- coding: utf-8 -*-

"""
checkout-server.manage
~~~~~~~~~~~~

"""
from flask_script import Manager
from checkout_server.app import create_app

manager = Manager(create_app())

if __name__ == "__main__":
    manager.run()
