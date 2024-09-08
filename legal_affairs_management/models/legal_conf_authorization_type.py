# -*- coding: utf-8 -*-

from odoo import models, fields


class LegalAuthorizationType(models.Model):
    _name = 'legal.authorization.type'
    _description = 'Legal Authorization Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    name = fields.Char(string="Authorization/Agency Type", required=True)
    type = fields.Selection([
        ('authorization', 'Authorization'),
        ('agency', 'Agency'),
    ], string="Type", required=True)
    description = fields.Text(string="Description")

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'Name already exists!')
    ]
