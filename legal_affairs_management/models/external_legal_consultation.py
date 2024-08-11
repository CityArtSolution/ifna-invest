# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class ExternalLegalConsultation(models.Model):
    _name = 'external.legal.consultation'
    _description = 'External Legal Consultation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    name = fields.Char(string="Consultation Number", required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    lawyer_id = fields.Many2one('legal.lawyer', string="Lawyer", required=True)
    consultation_date = fields.Datetime(string="Consultation Date", required=True)
    response = fields.Char(string="Lawyer Response")
    response_date = fields.Datetime(string="Response Date", required=True)
    attachment = fields.Binary(string="Attachment")
    attachment_filename = fields.Char(string="Attachment Filename")
    legal_consultation_type_id = fields.Many2one('legal.consultation.type', string="Consultation Type")
    document_status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('renewed', 'Renewed'),
        ('stop', 'Stop'),
    ], string="Document Status", default='draft')
    notes = fields.Text(string="Notes")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('external.legal.consultation') or 'New'
            vals['name'] = seq
        return super(ExternalLegalConsultation, self).create(vals)

    @api.onchange('consultation_date')
    def _onchange_consultation_date(self):
        if self.consultation_date:
            now = fields.Datetime.now()
            ten_minutes_later = now + timedelta(minutes=5)

            if self.consultation_date < ten_minutes_later:
                return {
                    'warning': {
                        'title': _('Past Date Warning'),
                        'message': _('The consultation date is in the past. Please check.'),
                    }
                }
