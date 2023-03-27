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
        super_user = self.env['res.users'].browse(SUPERUSER_ID)
        template_id = self.env.ref('rental_contract_notification.contract_notification_template')
        if template_id:
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

                            # todos = {
                            #     'res_id': i.id,
                            #     'res_model_id': self.env['ir.model'].search([('model', '=', 'your.model')]).id,
                            #     'user_id': email_to_custom.id,
                            #     'summary': 'your task title',
                            #     'note': 'your task message',
                            #     'activity_type_id': 4,
                            #     'date_deadline': fields.Date.today(),
                            # }
                            #
                            # self.env['mail.activity'].create(todos)

                            # mail = self.env['mail.message'].create({
                            #     'email_from': super_user.email,
                            #     'author_id': email_to_custom.partner_id.id,
                            #     'model': 'mail.channel',
                            #     'message_type': 'comment',
                            #     'subtype_id': self.env.ref('mail.mt_comment').id,
                            #     'subject': 'Contract Expired',
                            #     'body': f"""<p>Contract is about to expire <br/> """,
                            # })
                            # notification = {
                            #     'mail_message_id': mail.id,
                            #     'res_partner_id': email_to_custom.partner_id.id,
                            #     'notification_type': 'inbox',
                            #     'notification_status': 'sent',
                            # }
                            # mail.write({'notification_ids': [(0, 0, notification)]})
                            # print("///////////////")

                            # email_template_obj = self.env['mail.template'].browse(template_id.id)
                            # values = email_template_obj.generate_email(super_user.id,
                            #                                            ['subject', 'body_html', 'email_from', 'partner_to'])
                            # values['email_from'] = super_user.email
                            # values['email_to'] = email_to_custom.id
                            # values['res_id'] = False
                            # mail_mail_obj = self.env['mail.mail']
                            # msg_id = mail_mail_obj.create(values)
                            # if msg_id:
                            #     mail_mail_obj.send([msg_id])
