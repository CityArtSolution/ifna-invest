# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class ContractConfigurationSettings(models.TransientModel):
    _inherit = "res.config.settings"

    contract_expiry_days = fields.Integer(string="Contract Notification before (Days)")

    def get_values(self):
        res = super(ContractConfigurationSettings, self).get_values()
        contract_expiry_days = self.env['ir.config_parameter'].sudo().get_param(
            'rental_contract_notification.contract_expiry_days')
        res.update(
            contract_expiry_days=int(contract_expiry_days),
        )
        return res

    def set_values(self):
        super(ContractConfigurationSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('rental_contract_notification.contract_expiry_days',
                                                         str(self.contract_expiry_days))


class SalesInherit(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'portal.mixin',
                'mail.thread', 'mail.activity.mixin',
                'utm.mixin']

    def send_contract_end_notification(self):
        group = self.env.ref('rental_contract_notification.notify_group')
        contract_expiry_days = self.env['ir.config_parameter'].sudo().get_param(
            'rental_contract_notification.contract_expiry_days')
        if not int(contract_expiry_days):
            raise UserError('Please Configure Contract Expiry Notification Days In the Rental Configuration')
        notification_user = self.env['res.users'].search([]).filtered(lambda i: group in i.groups_id)
        contracts = self.env['sale.order'].search([('state', '=', 'sale')])
        if contracts:
            for i in contracts:
                diff = (i.todate.date() - fields.Date.today()).days
                if int(diff) == int(contract_expiry_days):
                    for email_to_custom in notification_user:
                        model_id = self.env['ir.model'].search(
                            [('model', '=', self._name)]).id
                        self.env['mail.activity'].with_user(email_to_custom.id).sudo().create({
                            'res_id': i.id,
                            'res_model_id': model_id,
                            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                            'summary': 'End of Contract Notification',
                            'note': f'Contract is about to End Please review and take appropriate action.',
                        })

                        self.message_subscribe(partner_ids=email_to_custom.partner_id.ids)
                        i.message_post(
                            body= f'Contract is about to End Please review and take appropriate action.',
                            subject='End of Contract Notification',
                            subtype_xmlid='mail.mt_comment',
                            message_type='comment',
                            partner_ids=email_to_custom.partner_id.ids)

