# -*- coding: utf-8 -*
from odoo import models, fields


class LegalCourt(models.Model):
    _name = 'legal.court'
    _description = 'Legal Court'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

    name = fields.Char(string="Name", required=True, tracking=True)
    court_level = fields.Selection([('primary', 'Primary Court'), ('appeal', 'Appeal Court')], string="Court Level", tracking=True)
