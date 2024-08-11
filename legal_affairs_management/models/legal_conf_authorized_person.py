# -*- coding: utf-8 -*-

from odoo import models, fields


class LegalAuthorizedPerson(models.Model):
    _name = 'legal.authorized.person'
    _description = 'Legal Authorized Person'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    name = fields.Char(string="Name", required=True)
    role = fields.Selection([
        ('employee', 'Employee'),
        ('company_rep', 'Company Representative'),
    ], string="Role", required=True)