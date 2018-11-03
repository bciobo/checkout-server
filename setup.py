# -*- coding: utf-8 -*-

"""
checkout-server.setup
~~~~~~~~~~~~

"""
import io
from os import path
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    readme = f.read()

REQUIRES = [
    'Flask==1.0.2',
]

setup(
    name='checkout-server',
    version='1.0.0',
    url='https://github.com/bciobo/checkout-server',
    license='MIT',
    maintainer='bciobo',
    maintainer_email='bogdan.ciobotaru1@gmail.com',
    description='Backend logic for handling Stripe orders for Doodance clients.',
    long_description=readme,
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRES,
    extras_require={
        'dev': ['pytest', 'coverage', 'flake8'],
    },
    python_requires='>=3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
