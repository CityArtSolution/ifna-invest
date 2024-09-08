# -*- coding: utf-8 -*-
from odoo import models, fields


class LegalLetter(models.Model):
    _name = 'legal.letter'
    _description = 'Legal Letter'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    name = fields.Char(required=True)

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'Name already exists!')
    ]


