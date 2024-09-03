# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta


class LegalCompanyDocument(models.Model):
    _name = 'legal.company.document'
    _description = 'Legal Company Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

    name = fields.Char(string="Document", required=True, tracking=True)
    issue_date = fields.Date(string="Issue Date", required=True, tracking=True)
    expiration_date = fields.Date(string="Expiration Date", required=True, tracking=True)
    attachment = fields.Binary(string="Document Attachment", tracking=True)
    attachment_filename = fields.Char(string="Attachment Filename", tracking=True)
    document_status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('in_preparation', 'In Preparation'),
        ('renewed', 'Renewed'),
    ], string="Document Status", required=True, default='draft', tracking=True)
    notes = fields.Text(string="Notes", tracking=True)
    chamber_of_commerce = fields.Char(string="Chamber of Commerce", tracking=True)
    national_address = fields.Char(string="National Address", tracking=True)
    chamber_of_commerce_subscription = fields.Char(string="Chamber of Commerce Subscription", tracking=True)
    real_estate_management_brokerage = fields.Char(string="Real Estate Management and Brokerage", tracking=True)
    commercial_registration = fields.Char(string="Commercial Registration", tracking=True)

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'Name already exists!')
    ]

    @api.model
    def _create_expiration_notification(self, document):
        notification_message = _(
            "The document '%s' for %s is expiring on %s."
        ) % (document.name, document.company_id.name, document.expiration_date.strftime('%Y-%m-%d'))

        self.env['mail.message'].create({
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_note').id,
            'body': notification_message,
            'model': 'company.document',
            'res_id': document.id,
            'partner_ids': [(6, 0, self.env.user.partner_id.ids)]
        })

    @api.model
    def _check_and_notify_expiring_documents(self):
        today = fields.Date.today()
        expiring_documents = self.search([
            ('expiration_date', '=', today + timedelta(days=30)),
            ('document_status', '!=', 'draft')
        ])
        for document in expiring_documents:
            self._create_expiration_notification(document)