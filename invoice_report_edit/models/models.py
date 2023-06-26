# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from .num_to_text_ar import amount_to_text_arabic


class ResBank(models.Model):
    _inherit = 'res.bank'

    iban = fields.Char(string='IBAN')
    swift = fields.Char(string='Swift')


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    iban = fields.Char(string='IBAN', related="bank_id.iban")
    swift = fields.Char(string='Swift', related="bank_id.swift")


class ExtendAccountMove(models.Model):
    _inherit = "account.move"

    def _convert_num_to_text(self, amount):
        return amount_to_text_arabic(abs(amount), 'SAR')
