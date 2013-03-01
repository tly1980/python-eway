import sys
import unittest
from decimal import Decimal

sys.path.insert(0, "./../../")

from eway import config
from eway.client import EwayPaymentClient
from eway.fields import Customer, CreditCard


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        # please change to your eway client
        self.eway_client = EwayPaymentClient('91728933',
                                             config.REAL_TIME_CVN,
                                             False,
                                             refund_password='xmlrefund123')

    def get_data(self):
        """
        Test the eWAY auth complete functionality.
        """
        customer = Customer()
        customer.first_name = "Joe"
        customer.last_name = "Bloggs"
        customer.email = "name@xyz.com.au"
        customer.address = "123 Someplace Street, Somewhere ACT"
        customer.postcode = "2609"
        customer.invoice_description = "Testing"
        customer.invoice_reference = "INV120394"
        customer.country = "AU"

        credit_card = CreditCard()
        credit_card.holder_name = '%s %s' % (customer.first_name, customer.last_name,)
        credit_card.number = "4444333322221111"
        credit_card.expiry_month = 10
        credit_card.expiry_year = 15
        credit_card.verification_number = "123"
        credit_card.ip_address = "127.0.0.1"

        return [customer, credit_card]

    def test_refund(self):
        """
        Test the eWAY payment functionality.
        """
        customer, credit_card = self.get_data()

        # step 1, make a payment

        response = self.eway_client.payment(
            Decimal("10.08"),
            credit_card=credit_card,
            customer=customer,
            reference="123456"
        )

        self.failUnless(response.success)
        self.assertIn('Honour With Identification', response.get_message())
        self.failUnlessEqual('08', response.get_code(), 'Response code should be 08')

        resp_refund = self.eway_client.refund(
            Decimal('10.08'),
            response.transaction_number
        )

        self.failUnless(resp_refund.success)
        self.assertIsNotNone(resp_refund.transaction_number)
        self.failUnlessEqual('00', resp_refund.get_code())

    def test_refund_multiple(self):
        """
        Test the eWAY payment functionality.
        """
        customer, credit_card = self.get_data()

        # step 1, make a payment

        response = self.eway_client.payment(
            Decimal("20"),
            credit_card=credit_card,
            customer=customer,
            reference="123456"
        )

        self.failUnless(response.success)

        # reminding: $20
        resp_refund = self.eway_client.refund(
            Decimal('10'),
            response.transaction_number)

        self.assertTrue(resp_refund.success)
        self.assertIsNotNone(resp_refund.transaction_number)

        # reminding: $10. this one should failed.
        resp_refund = self.eway_client.refund(
            Decimal('15'),
            response.transaction_number,
        )
        self.assertFalse(resp_refund.success)

        # reminding: $10
        resp_refund = self.eway_client.refund(
            Decimal('7'),
            response.transaction_number
        )

        self.assertTrue(resp_refund.success)

        # reminding: $3
        resp_refund = self.eway_client.refund(
            Decimal('3.01'),
            response.transaction_number
        )

        self.assertFalse(resp_refund.success)

        # reminding: $3
        resp_refund = self.eway_client.refund(
            Decimal('3.00'),
            response.transaction_number
        )

        self.assertTrue(resp_refund.success)


if __name__ == '__main__':
    unittest.main()

