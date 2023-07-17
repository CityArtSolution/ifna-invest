# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager


class CustomerPortal(portal.CustomerPortal):

    #
    # Quotations and Sales Orders
    #

    @http.route(['/my/orders/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, order_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        # if not order_sudo.has_to_be_signed():
        #     return {'error': _('The order is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            order_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        if not order_sudo.has_to_be_paid():
            order_sudo.action_initial_contract()
            # order_sudo.action_confirm()
            # order_sudo._send_order_confirmation_mail()

        pdf = request.env.ref('sale.action_report_saleorder').with_user(SUPERUSER_ID)._render_qweb_pdf([order_sudo.id])[0]

        _message_post_helper(
            'sale.order', order_sudo.id, _('Order signed by %s') % (name,),
            attachments=[('%s.pdf' % order_sudo.name, pdf)],
            **({'token': access_token} if access_token else {}))

        query_string = '&message=sign_ok'
        if order_sudo.has_to_be_paid(True):
            query_string += '#allow_payment=yes'
        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }

    @http.route(['/my/orders/<int:order_id>/decline'], type='http', auth="public", methods=['POST'], website=True)
    def decline(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message = post.get('decline_message')

        query_string = False
        if order_sudo.has_to_be_signed() and message:
            order_sudo.action_cancel()
            _message_post_helper('sale.order', order_id, message, **{'token': access_token} if access_token else {})
        else:
            query_string = "&message=cant_reject"

        return request.redirect(order_sudo.get_portal_url(query_string=query_string))


class PaymentPortal(payment_portal.PaymentPortal):

    @http.route('/my/orders/<int:order_id>/transaction', type='json', auth='public')
    def portal_order_transaction(self, order_id, access_token, **kwargs):
        """ Create a draft transaction and return its processing values.

        :param int order_id: The sales order to pay, as a `sale.order` id
        :param str access_token: The access token used to authenticate the request
        :param dict kwargs: Locally unused data passed to `_create_transaction`
        :return: The mandatory values for the processing of the transaction
        :rtype: dict
        :raise: ValidationError if the invoice id or the access token is invalid
        """
        # Check the order id and the access token
        try:
            self._document_check_access('sale.order', order_id, access_token)
        except MissingError as error:
            raise error
        except AccessError:
            raise ValidationError("The access token is invalid.")

        kwargs.update({
            'reference_prefix': None,  # Allow the reference to be computed based on the order
            'sale_order_id': order_id,  # Include the SO to allow Subscriptions tokenizing the tx
        })
        kwargs.pop('custom_create_values', None)  # Don't allow passing arbitrary create values
        tx_sudo = self._create_transaction(
            custom_create_values={'sale_order_ids': [Command.set([order_id])]}, **kwargs,
        )

        return tx_sudo._get_processing_values()

    # Payment overrides

    @http.route()
    def payment_pay(self, *args, amount=None, sale_order_id=None, access_token=None, **kwargs):
        """ Override of payment to replace the missing transaction values by that of the sale order.

        This is necessary for the reconciliation as all transaction values, excepted the amount,
        need to match exactly that of the sale order.

        :param str amount: The (possibly partial) amount to pay used to check the access token
        :param str sale_order_id: The sale order for which a payment id made, as a `sale.order` id
        :param str access_token: The access token used to authenticate the partner
        :return: The result of the parent method
        :rtype: str
        :raise: ValidationError if the order id is invalid
        """
        # Cast numeric parameters as int or float and void them if their str value is malformed
        amount = self._cast_as_float(amount)
        sale_order_id = self._cast_as_int(sale_order_id)
        if sale_order_id:
            order_sudo = request.env['sale.order'].sudo().browse(sale_order_id).exists()
            if not order_sudo:
                raise ValidationError(_("The provided parameters are invalid."))

            # Check the access token against the order values. Done after fetching the order as we
            # need the order fields to check the access token.
            if not payment_utils.check_access_token(
                access_token, order_sudo.partner_id.id, amount, order_sudo.currency_id.id
            ):
                raise ValidationError(_("The provided parameters are invalid."))

            kwargs.update({
                'currency_id': order_sudo.currency_id.id,
                'partner_id': order_sudo.partner_id.id,
                'company_id': order_sudo.company_id.id,
                'sale_order_id': sale_order_id,
            })
        return super().payment_pay(*args, amount=amount, access_token=access_token, **kwargs)

    def _get_custom_rendering_context_values(self, sale_order_id=None, **kwargs):
        """ Override of payment to add the sale order id in the custom rendering context values.

        :param int sale_order_id: The sale order for which a payment id made, as a `sale.order` id
        :return: The extended rendering context values
        :rtype: dict
        """
        rendering_context_values = super()._get_custom_rendering_context_values(**kwargs)
        if sale_order_id:
            rendering_context_values['sale_order_id'] = sale_order_id
        return rendering_context_values

    def _create_transaction(self, *args, sale_order_id=None, custom_create_values=None, **kwargs):
        """ Override of payment to add the sale order id in the custom create values.

        :param int sale_order_id: The sale order for which a payment id made, as a `sale.order` id
        :param dict custom_create_values: Additional create values overwriting the default ones
        :return: The result of the parent method
        :rtype: recordset of `payment.transaction`
        """
        if sale_order_id:
            if custom_create_values is None:
                custom_create_values = {}
            # As this override is also called if the flow is initiated from sale or website_sale, we
            # need not to override whatever value these modules could have already set
            if 'sale_order_ids' not in custom_create_values:  # We are in the payment module's flow
                custom_create_values['sale_order_ids'] = [Command.set([int(sale_order_id)])]

        return super()._create_transaction(
            *args, sale_order_id=sale_order_id, custom_create_values=custom_create_values, **kwargs
        )
