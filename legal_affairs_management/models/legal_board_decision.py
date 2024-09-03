# -*- coding: utf-8 -*
from odoo import models, fields


class LegalBoardDecision(models.Model):
    _name = 'legal.board.decision'
    _description = 'Legal Board Decision'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

    name = fields.Char(string="Decision Subject", required=True, tracking=True)
    decision_date = fields.Date(string="Decision Date", required=True, tracking=True)
    attachment = fields.Binary(string="Decision Attachment")
    attachment_filename = fields.Char(string="Attachment Filename")
    document_status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
    ], string="Document Status", required=True, default='draft', tracking=True)
    notes = fields.Text(string="Notes")

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'Name already exists!')
    ]

