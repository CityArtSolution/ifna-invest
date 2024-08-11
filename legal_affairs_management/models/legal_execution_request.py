# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LegalExecutionRequest(models.Model):
    _name = 'legal.execution.request'
    _description = 'Legal Execution Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    name = fields.Char(string="Request Number", required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    plaintiff = fields.Char(string="Plaintiff", tracking=True)
    partner_id = fields.Many2one('res.partner', string="Defendant", domain=[('is_legal_defendant', '=', True)], required=True)
    execution_amount = fields.Monetary(string="Execution Amount", currency_field='currency_id', related="partner_id.total_overdue_amount", readonly=False)
    court_id = fields.Many2one('legal.court', string="Court Name", tracking=True)
    execution_number = fields.Char(string="Execution Number")
    document_status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('submitted', 'Submitted'),
    ], string="Document Status", default='draft')
    notes = fields.Text(string="Notes")
    attachment = fields.Binary(string="Attachment")
    attachment_filename = fields.Char(string="Attachment Filename")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)

    # States for notifications and actions
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
    ], string='State', default='draft')

    # Trigger to notify the manager if document status is changed
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('legal.execution.request') or 'New'
            vals['name'] = seq
        record = super(LegalExecutionRequest, self).create(vals)
        if record.document_status == 'approved':
            self._send_notification(record)
        return record

    def _send_notification(self, record):
        # Define the message body
        message_body = f"Execution Request #{record.name} has been approved. Please review it."

        # Create the notification
        self.env['mail.message'].create({
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_note').id,
            'body': message_body,
            'model': 'execution.request',
            'res_id': record.id,
            'partner_ids': [(6, 0, [self.env.user.partner_id.id])]
        })

    @api.onchange('execution_amount')
    def _onchange_execution_amount(self):
        # Check if execution amount is more than 100,000, show a warning
        if self.execution_amount > 100000:
            return {
                'warning': {
                    'title': 'High Amount Warning',
                    'message': 'The execution amount is very high. Please double-check.',
                }
            }
