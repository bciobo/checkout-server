# -*- coding: utf-8 -*-

"""
checkout-server.resources
~~~~~~~~~~~~

"""
import json
from stripe.error import InvalidRequestError
from flask.views import MethodView
from flask import current_app as app, jsonify, abort, request


def dynamic_3ds(stripe, source, order):
    """
    Create a 3DS Secure payment Source if the Source is a card that requires it or if the Order is over 5000.
    """
    if source['card']['three_d_secure'] == 'required' or order['amount'] > 5000:
        source = stripe.Source.create(amount=order['amount'], currency=order['currency'], type='three_d_secure',
                                      three_d_secure={'card': source['id']}, metadata={'order': order['id']},
                                      redirect={'return_url': request.headers.get('origin')})
    return source


class CheckoutView(MethodView):
    def __init__(self, stripe):
        self.stripe = stripe


class ConfigResource(MethodView):
    """
    Retrieve form config and Stripe publishable key.
    """
    def get(self):
        config = {'country': app.config.get('CHECKOUT_COUNTRY', 'DE'),
                  'currency': app.config.get('CHECKOUT_CURRENCY', 'eur'),
                  'stripePublishableKey': app.config.get('PUBLISHABLE_KEY', '')}
        return jsonify(config)


class ProductsResource(CheckoutView):
    """
    Retrieve all or one product.
    """
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
                abort(404, 'Doodance: product ID is unknown')


class OrdersResource(CheckoutView):
    """
    Retrieve order data.
    """
    def get(self, order_id):
        try:
            return jsonify(self.stripe.Order.retrieve(order_id))
        except InvalidRequestError as invalid_req_err:
            app.logger.error(invalid_req_err.json_body.get('error'))
        except Exception as e:
            app.logger.error(e)
            abort(404, 'Doodance: order ID is unknown')

    def post(self):
        """
        Create new order.
        """
        try:
            form_data = json.loads(request.data)
            new_order = self.stripe.Order.create(
                currency=form_data.get('currency'),
                items=form_data.get('items'),
                email=form_data.get('email'),
                metadata={'country': form_data.get('country'), 'customer': form_data.get('customer')}
            )

            return jsonify({'order': new_order})

        except Exception as e:
            app.logger.error(e)
            abort(404, 'Doodance: error while creating order')


class PayOrdersResource(CheckoutView):
    """
    Pay an order.
    """

    def post(self, order_id):
        if not order_id:
            abort(404, 'Doodance: no order ID given')
        request_data = json.loads(request.data)
        source = request_data.get('source')
        try:
            # fetch order data
            order = self.stripe.Order.retrieve(order_id)
            # check that order was not already paid
            if order['status'] in ['pending', 'paid']:
                abort(403, 'Doodance: order does not need to be paid')
            source_type = source.get('type')
            # apply 3DS for card payments
            if source_type and source_type == 'card':
                source = dynamic_3ds(self.stripe, source, order)
            # pay order
            source_status = source.get('status')
            if source_status and source_status == 'chargeable':
                order.pay(source=source['id'])
            elif source_status and source_status == 'pending' or source_status == 'paid':
                # Somehow this Order has already been paid for -- abandon request.
                return jsonify({'source': source, 'order': order})
            else:
                app.logger.error('The source was not chargeable: %s, for order %s' % (source, order))
                abort(404, 'Doodance: the source was not chargeable')

            return jsonify({'order': order, 'source': source})

        except InvalidRequestError as invalid_req_err:
            app.logger.error(invalid_req_err.json_body.get('error'))
            abort(404, 'Doodance: order ID is unknown')
        except Exception as e:
            app.logger.error(e)
            abort(jsonify(error='Doodance: error while paying order %s' % e))


class Webhook(CheckoutView):
    """
    Webhook for handling events:
    - source.chargeable
    - source.failed
    - source.canceled
    - charge.failed
    - charge.succeeded

    It pays the order or update the order metadata according to status of source/charge.
    """
    def post(self):
        event = json.loads(request.data)
        webhook_secret = app.config.get('WEBHOOK_SECRET')

        if not webhook_secret:
            app.logger.warning('Doodance: Stripe webhook secret not configured.')
            data = event['data']
        else:
            signature = request.headers.get('stripe-signature')
            try:
                event = self.stripe.Webhook.construct_event(payload=request.data,
                                                            sig_header=signature,
                                                            secret=webhook_secret)
                data = event['data']
            except Exception as e:
                app.logger.error('Webhook signature verification failed %s' % e)
                abort(404, 'Doodance: Webhook signature verification failed')

        data_object = data['object']

        # Monitor `source.chargeable` events.
        if data_object['object'] == 'source' \
                and data_object['status'] == 'chargeable' \
                and 'order' in data_object['metadata']:
            source = data_object
            app.logger.info('Doodance: Webhook received! The source %s is chargeable' % source["id"])
            # Get the order data
            order = self.stripe.Order.retrieve(source['metadata']['order'])
            # Check the order is payable
            order_status = order['metadata']['status']
            if order_status in ['pending', 'paid', 'failed']:
                abort(404, 'Doodance: Order cannot be paid because it has status "%s"' % order_status)
            # Pay the order
            order.pay(source=source['id'])

        # Monitor `charge.succeeded` events.
        if data_object['object'] == 'charge' \
                and data_object['status'] == 'succeeded' \
                and 'order' in data_object['source']['metadata']:
            charge = data_object
            app.logger.info('Doodance: Webhook received! The charge %s succeeded' % charge["id"])
            # Get the order data
            order = self.stripe.Order.retrieve(charge['metadata']['order'])
            # Update the order metadata
            order.metadata['status'] = 'paid'
            order.save()

        # Monitor `source.failed`, `source.canceled`, and `charge.failed` events.
        if event['type'] in ['source.failed', 'source.canceled', 'charge.failed'] or \
                (data_object['object'] in ['source', 'charge'] and data_object['status'] in ['failed', 'canceled']):

            app.logger.info('Doodance: Webhook received! Failure for %s' % data_object["id"])

            if data_object['metadata'].get('order'):
                # Get the order data
                order = self.stripe.Order.retrieve(data_object['metadata']['order'])
                # Update the order metadata
                order.metadata['status'] = 'failed'
                order.save()

            return jsonify({'status': 'failed'})

        return jsonify({'status': 'success'})
