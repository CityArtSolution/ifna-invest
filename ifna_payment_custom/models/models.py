
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class PaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    employee_id = fields.Many2one(comodel_name="account.analytic.account", string="Employee", required=False, )
