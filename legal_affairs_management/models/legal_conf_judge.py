# -*- coding: utf-8 -*
from odoo import models, fields


class LegalJudge(models.Model):
    _name = 'legal.judge'
    _description = 'Legal Judge'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

    name = fields.Char(string="Name", required=True, tracking=True)