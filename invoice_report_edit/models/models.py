# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from .num_to_text_ar import amount_to_text_arabic


class ResBank(models.Model):
    _inherit = 'res.bank'

    iban = fields.Char(string='Iban')


class ExtendAccountMove(models.Model):
    _inherit = "account.move"

    def _convert_num_to_text(self, amount):
        return amount_to_text_arabic(abs(amount), 'SAR')
