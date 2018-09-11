# -*- coding: utf-8 -*-

"""
checkout-server.setup
~~~~~~~~~~~~

"""
import io
from os import path
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

with open(path.join(here, 'requirements.txt')) as f:
    requirements = [line for line in f.read().split('\n') if line]

setup(
    name='checkout-server',
    version='1.0.0',
    url='https://github.com/bciobo/checkout-server',
    license='MIT',
    maintainer='bciobo',
    maintainer_email='bogdan.ciobotaru1@gmail.com',
    description='Backend logic for handling Stripe orders for Doodance clients.',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
)
