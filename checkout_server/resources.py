# -*- coding: utf-8 -*-

"""
checkout-server.resources
~~~~~~~~~~~~

"""
import json
from stripe.error import InvalidRequestError
from flask.views import MethodView
from flask import current_app as app
from flask import jsonify, abort, request, send_from_directory, make_response
from checkout_server.models import InvalidCouponError, InvalidAmountError


def dynamic_3ds(stripe, source, order, amount):
    """
    Create a 3DS Secure payment Source if the Source is a card that requires it or if the Order is over 5000.
    """
    if source['card']['three_d_secure'] == 'required' or amount > 5000:
        source = stripe.Source.create(amount=amount, currency=order['currency'], type='three_d_secure',
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
                print(invalid_req_err.json_body.get('error'))
            except Exception as e:
                print(e)
                abort(404, 'Doodance: product ID is unknown')


class OrdersResource(CheckoutView):
    """
    Retrieve order data.
    """

    def get(self, order_id):
        try:
            return jsonify(self.stripe.Order.retrieve(order_id))
        except InvalidRequestError as invalid_req_err:
            print(invalid_req_err.json_body.get('error'))
        except Exception as e:
            print(e)
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
            print(e)
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
        coupon_code = request_data.get('coupon_code')
        new_price = request_data.get('new_price')
        try:
            # fetch order data
            order = self.stripe.Order.retrieve(order_id)
            # check that order was not already paid
            if order['status'] in ['pending', 'paid']:
                abort(403, 'Doodance: order does not need to be paid')
            source_type = source.get('type')
            # apply 3DS for card payments
            if source_type and source_type == 'card':
                amount = new_price if new_price else order['amount']
                source = dynamic_3ds(self.stripe, source, order, amount)
            # pay order
            if new_price:
                source = self.stripe.Source.retrieve(source['id'])
                charge = self.stripe.Charge.create(
                    amount=new_price,  # TODO: make sure it's in the right format i.e.: 2000 = 20.0
                    currency=order['currency'],
                    source=source,
                    metadata={'order_id': order['id'],
                              'customer': order['metadata']['customer'],
                              'coupon_code': coupon_code}
                )
                if charge['paid'] or (charge['captured'] and charge['status'] == 'pending'):
                    updated_order = self.stripe.Order.modify(order['id'], metadata={'charge_id': charge['id'],
                                                                                    'coupon_code': coupon_code,
                                                                                    'status': 'paid'})
                    updated_order['status'] = 'paid'
                    return jsonify({'order': updated_order, 'source': source})
                else:
                    print('The charge was not paid: %s, for order %s' % (charge, order))
                    abort(404, 'Doodance: the charge was not paid')
            else:
                source_status = source.get('status')
                if source_status and source_status == 'chargeable':
                    order.pay(source=source['id'])
                elif source_status and source_status == 'pending' or source_status == 'paid':
                    # Somehow this Order has already been paid for -- abandon request.
                    return jsonify({'source': source, 'order': order})
                else:
                    print('The source was not chargeable: %s, for order %s' % (source, order))
                    abort(404, 'Doodance: the source was not chargeable')

                return jsonify({'order': order, 'source': source})

        except InvalidRequestError as invalid_req_err:
            print(invalid_req_err.json_body.get('error'))
            abort(404, 'Doodance: order ID is unknown')


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

    def __init__(self, stripe, coupon_cms):
        super(Webhook, self).__init__(stripe)
        self.coupon_cms = coupon_cms

    def post(self):
        event = json.loads(request.data)
        webhook_secret = app.config.get('WEBHOOK_SECRET')

        if not webhook_secret:
            print('Doodance: Stripe webhook secret not configured.')
            data = event['data']
        else:
            signature = request.headers.get('stripe-signature')
            try:
                event = self.stripe.Webhook.construct_event(payload=request.data,
                                                            sig_header=signature,
                                                            secret=webhook_secret)
                data = event['data']
            except Exception as e:
                print('Webhook signature verification failed %s' % e)
                abort(404, 'Doodance: Webhook signature verification failed')

        data_object = data['object']

        # Monitor `source.chargeable` events.
        if data_object['object'] == 'source' \
                and data_object['status'] == 'chargeable' \
                and 'order' in data_object['metadata']:
            source = data_object
            print('Doodance: Webhook received! The source %s is chargeable' % source["id"])
            # Get the order data
            order = self.stripe.Order.retrieve(source['metadata']['order'])
            # Check the order is payable
            order_status = order.get('status')
            order_metadata_status = order['metadata'].get('status')
            if order_status in ['pending', 'paid', 'failed'] or order_metadata_status in ['pending', 'paid', 'failed']:
                abort(404, 'Doodance: Order cannot be paid because it has status "%s"' % order_status)
            # Pay the order
            order.pay(source=source['id'])

        # Monitor `charge.succeeded` events.
        if data_object['object'] == 'charge' \
                and data_object['status'] == 'succeeded' \
                and 'order_id' in data_object['metadata']:
            charge = data_object
            print('Doodance: Webhook received! The charge %s succeeded' % charge["id"])
            # Get the order data
            order = self.stripe.Order.retrieve(charge['metadata']['order_id'])
            # Update the order metadata
            coupon_code = charge['metadata'].get('coupon_code')
            self.stripe.Order.modify(order['id'], metadata={'charge_id': charge['id'],
                                                            'coupon_code': coupon_code,
                                                            'status': 'paid'})
            if coupon_code:
                self.coupon_cms.use_once(coupon=self.coupon_cms.get_coupon_by_code(coupon_code))

        # Monitor `source.failed`, `source.canceled`, and `charge.failed` events.
        if event['type'] in ['source.failed', 'source.canceled', 'charge.failed'] or \
                (data_object['object'] in ['source', 'charge'] and data_object['status'] in ['failed', 'canceled']):

            print('Doodance: Webhook received! Failure for %s' % data_object["id"])
            order_id = data_object['metadata'].get('order_id')
            if order_id:
                # Update the order metadata
                self.stripe.Order.modify(order_id, metadata={'charge_id': data_object['id'],
                                                             'coupon_code': data_object['metadata'].get(
                                                                 'coupon_code'),
                                                             'status': 'failed'})
            return jsonify({'status': 'failed'})

        return jsonify({'status': 'success'})


class Bundle(MethodView):
    def get(self, filename):
        return send_from_directory('bundle', filename)


class CouponResource(MethodView):
    def __init__(self, coupon_cms):
        self.coupon_cms = coupon_cms

    def post(self):
        request_data = json.loads(request.data)
        coupon_code = request_data.get('code')
        price = request_data.get('price')

        if not coupon_code or not price:
            return abort(make_response(('Fehler: bitte kontaktieren Sie uns unter kontakt@doodance.com.', 400)))

        price = float(price)
        coupon = self.coupon_cms.get_coupon_by_code(coupon_code)

        if not coupon:
            return abort(make_response(('Gutschein Code existiert nicht.', 404)))
        try:
            new_price = coupon.apply(price)
        except InvalidAmountError:
            return abort(make_response(('Fehler: bitte kontaktieren Sie uns unter kontakt@doodance.com.', 400)))
        except InvalidCouponError:
            return abort(make_response(('Gutschein Code ist abgelaufen.', 403)))

        return jsonify({'new_price': round(new_price, 2), 'discount': round(price - new_price, 2)})
