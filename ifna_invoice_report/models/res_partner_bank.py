# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    iban = fields.Char(string='Iban')
    swift = fields.Char(string='Swift')


class NewModule(models.Model):
    _inherit = 'account.move'


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_bank = fields.Many2one('res.partner.bank', string="Default Bank Account")
