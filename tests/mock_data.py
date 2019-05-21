# -*- coding: utf-8 -*-

"""
checkout-server.tests.mock_data
~~~~~~~~~~~~

"""


class DictWithPay(dict):
    def pay(self, *args, **kwargs):
        pass


ORDER_CREATED = DictWithPay({
    "amount": 6900,
    "amount_returned": None,
    "application": None,
    "application_fee": None,
    "charge": None,
    "created": 1546981925,
    "currency": "eur",
    "customer": None,
    "email": "b.ciobotaru@solvemate.com",
    "id": "or_1DqRrlGficNruBuglAh0ZkMZ",
    "items": [
        {
            "amount": 6900,
            "currency": "eur",
            "description": "Langsamer Walzer",
            "object": "order_item",
            "parent": "sku_CSRZlrX4AgHio6",
            "quantity": 1,
            "type": "sku"
        },
        {
            "amount": 0,
            "currency": "eur",
            "description": "Taxes (included)",
            "object": "order_item",
            "parent": None,
            "quantity": None,
            "type": "tax"
        },
        {
            "amount": 0,
            "currency": "eur",
            "description": "Free shipping",
            "object": "order_item",
            "parent": "ship_free-shipping",
            "quantity": None,
            "type": "shipping"
        }
    ],
    "livemode": False,
    "metadata": {
        "country": "Deutschland",
        "customer": "bogdan"
    },
    "object": "order",
    "returns": {
        "data": [],
        "has_more": False,
        "object": "list",
        "total_count": 0,
        "url": "/v1/order_returns?order=or_1DqRrlGficNruBuglAh0ZkMZ"
    },
    "selected_shipping_method": "ship_free-shipping",
    "shipping": None,
    "shipping_methods": [
        {
            "amount": 0,
            "currency": "eur",
            "delivery_estimate": None,
            "description": "Free shipping",
            "id": "ship_free-shipping"
        }
    ],
    "status": "created",
    "status_transitions": {
        "canceled": None,
        "fulfiled": None,
        "paid": None,
        "returned": None
    },
    "updated": 1546981925
})

SOURCE_VISA = {
    "amount": None,
    "card": {
        "address_line1_check": None,
        "address_zip_check": "pass",
        "brand": "Visa",
        "country": "US",
        "cvc_check": "pass",
        "dynamic_last4": None,
        "exp_month": 4,
        "exp_year": 2024,
        "fingerprint": "ai22gbW9ymgDL481",
        "funding": "credit",
        "last4": "4242",
        "name": None,
        "three_d_secure": "optional",
        "tokenization_method": None
    },
    "client_secret": "src_client_secret_Dwv1gCOexIsD3qvDx5zB61qg",
    "created": 1541874470,
    "currency": None,
    "flow": "none",
    "id": "src_1DV1BSGficNruBugV4VCeZeg",
    "livemode": False,
    "metadata": {
        "course": "Wiener Walzer"
    },
    "object": "source",
    "owner": {
        "address": {
            "city": None,
            "country": None,
            "line1": None,
            "line2": None,
            "postal_code": "32131",
            "state": None
        },
        "email": None,
        "name": "Boggi",
        "phone": None,
        "verified_address": None,
        "verified_email": None,
        "verified_name": None,
        "verified_phone": None
    },
    "statement_descriptor": None,
    "status": "chargeable",
    "type": "card",
    "usage": "reusable"
}

CHARGE = {
    "amount": 2000,
    "amount_refunded": 0,
    "application": None,
    "application_fee": None,
    "application_fee_amount": None,
    "balance_transaction": "txn_1EVlXyGficNruBugpY7KwP41",
    "billing_details": {
        "address": {
            "city": None,
            "country": None,
            "line1": None,
            "line2": None,
            "postal_code": None,
            "state": None
        },
        "email": None,
        "name": None,
        "phone": None
    },
    "captured": True,
    "created": 1556829025,
    "currency": "eur",
    "customer": None,
    "description": "Charge for jenny.rosen@example.com",
    "destination": None,
    "dispute": None,
    "failure_code": None,
    "failure_message": None,
    "fraud_details": {},
    "id": "ch_1EVlXxGficNruBug4SgfxqwG",
    "invoice": None,
    "livemode": False,
    "metadata": {},
    "object": "charge",
    "on_behalf_of": None,
    "order": None,
    "outcome": {
        "network_status": "approved_by_network",
        "reason": None,
        "risk_level": "normal",
        "risk_score": 26,
        "seller_message": "Payment complete.",
        "type": "authorized"
    },
    "paid": True,
    "payment_intent": None,
    "payment_method": "card_1EVlXxGficNruBugvbt7ZhtY",
    "payment_method_details": {
        "card": {
            "brand": "visa",
            "checks": {
                "address_line1_check": None,
                "address_postal_code_check": None,
                "cvc_check": None
            },
            "country": "US",
            "description": "Visa Classic",
            "exp_month": 5,
            "exp_year": 2020,
            "fingerprint": "ai22gbW9ymgDL481",
            "funding": "credit",
            "last4": "4242",
            "three_d_secure": None,
            "wallet": None
        },
        "type": "card"
    },
    "receipt_email": None,
    "receipt_number": None,
    "receipt_url": "https://pay.stripe.com/receipts/acct_1AxfJ8GficNruBug/ch_1EVlXxGficNruBug4SgfxqwG/rcpt_"
                   "Ezl4J1j8a34gvK1XCWuZNzvq1SJJX3z",
    "refunded": False,
    "refunds": {
        "data": [],
        "has_more": False,
        "object": "list",
        "total_count": 0,
        "url": "/v1/charges/ch_1EVlXxGficNruBug4SgfxqwG/refunds"
    },
    "review": None,
    "shipping": None,
    "source": {
        "address_city": None,
        "address_country": None,
        "address_line1": None,
        "address_line1_check": None,
        "address_line2": None,
        "address_state": None,
        "address_zip": None,
        "address_zip_check": None,
        "brand": "Visa",
        "country": "US",
        "customer": None,
        "cvc_check": None,
        "dynamic_last4": None,
        "exp_month": 5,
        "exp_year": 2020,
        "fingerprint": "ai22gbW9ymgDL481",
        "funding": "credit",
        "id": "card_1EVlXxGficNruBugvbt7ZhtY",
        "last4": "4242",
        "metadata": {},
        "name": None,
        "object": "card",
        "tokenization_method": None
    },
    "source_transfer": None,
    "statement_descriptor": None,
    "status": "succeeded",
    "transfer_data": None,
    "transfer_group": None
}
