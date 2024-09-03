# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LegalConsultationType(models.Model):
    _name = 'legal.consultation.type'
    _description = 'Legal Consultation Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    name = fields.Char(string="Name")

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'Name already exists!')
    ]