from mollie.api.client import Client as MollieClient

from odoo import models, service


class PaymentAcquirerMollie(models.Model):
    _inherit = "payment.provider"

    def _api_mollie_create_customer_id(self):
        if self._context.get("partner", False):
            partner = self.env["res.partner"].browse(self._context.get("partner"))
            customer_data = {
                "name": partner.name,
                "metadata": {"odoo_partner_id": partner.id},
            }
            if partner.email:
                customer_data["email"] = partner.email
            return self._mollie_make_request(
                "/customers", data=customer_data, method="POST"
            )
        return super(PaymentAcquirerMollie, self)._api_mollie_create_customer_id()

    def _mollie_get_supported_methods(
        self, order, invoice, amount, currency, partner_id
    ):
        """
        Show only credit card payment method when checkout subscriptions type products
        """
        methods = super(PaymentAcquirerMollie, self)._mollie_get_supported_methods(
            order, invoice, amount, currency, partner_id
        )
        if (order and order.group_subscription_lines()) or (
            invoice and invoice.subscription_id
        ):
            methods = methods.filtered(
                lambda m: m.method_code in ["creditcard", "ideal"]
            )
        return methods

    def _api_mollie_get_client(self):
        mollie_client = MollieClient(timeout=10)
        if self.state == "enabled":
            mollie_client.set_api_key(self.mollie_api_key)
        elif self.state == "test":
            mollie_client.set_api_key(self.mollie_api_key_test)

        mollie_client.set_user_agent_component(
            "Odoo", service.common.exp_version()["server_version"]
        )
        mollie_client.set_user_agent_component(
            "MollieOdoo", self.env.ref("base.module_payment_mollie").installed_version
        )
        return mollie_client
