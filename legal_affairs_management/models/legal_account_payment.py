# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LegalAccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    case_id = fields.Many2one('legal.case', 'Case', tracking=True)
    is_legal_payment = fields.Boolean("Belongs Legal")
