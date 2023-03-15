# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from .num_to_text_ar import amount_to_text_arabic


class ResBank(models.Model):
    _inherit = 'res.bank'

    iban = fields.Char(string='Iban')
    holder_name = fields.Many2one("res.partner",string='Holder Name')
    #
    # def get_holder_name(self):
    #     for rec in self:
    #         banks = self.env['res.partner.bank'].search([('bank_id', '=', rec.id)], limit=1)
    #         rec.holder_name = banks.partner_id.id


class ExtendAccountMove(models.Model):
    _inherit = "account.move"

    def _convert_num_to_text(self, amount):
        return amount_to_text_arabic(abs(amount), 'SAR')
