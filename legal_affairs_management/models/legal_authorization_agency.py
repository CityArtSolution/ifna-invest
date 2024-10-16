# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
from datetime import timedelta
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class LegalAuthorizationAgency(models.Model):
    _name = 'legal.authorization.agency'
    _description = 'Legal Authorization and Agency'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    name = fields.Char(string="Document", required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)
    partner_id = fields.Many2one('res.partner', string="Defendant", required=True, domain=[('is_legal_defendant', '=', True)], tracking=True)
    authorized_person_id = fields.Many2one('res.partner', string="Authorized", domain=[('is_legal_authorized', '=', True)], tracking=True)
    authorized_role = fields.Selection([
        ('employee', 'Employee'),
        ('company_rep', 'Company Representative'),
    ], string="Authorized Role", compute="_compute_authorized_role", store=True, tracking=True)
    authorization_type = fields.Selection([
        ('agency', 'Agency'),
        ('authorization', 'Authorization'),
    ], string="Type", required=True, tracking=True)
    start_date = fields.Date(string="Start Date", required=True, tracking=True)
    end_date = fields.Date(string="End Date", required=True, tracking=True)
    attachment = fields.Binary(string="Attachment", tracking=True)
    attachment_filename = fields.Char(string="Attachment Filename", tracking=True)
    document_status = fields.Selection([
        ('draft', 'Draft'),
        ('renewed', 'Renewed'),
        ('cancelled', 'Cancelled'),
        ('stop', 'Stop'),
    ], string="Document Status", default='draft', required=True, tracking=True)
    notes = fields.Text(string="Notes", tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('legal.authorization.agency') or 'New'
        return super(LegalAuthorizationAgency, self).create(vals)

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date <= fields.Date.today():
            return {
                'warning': {
                    'title': _('End Date Warning'),
                    'message': _('The end date is in the past or today. Please check.'),
                }
            }

    @api.depends('authorized_person_id')
    def _compute_authorized_role(self):
        for record in self:
            if record.authorized_person_id:
                if record.authorized_person_id.company_type == 'person':
                    record.authorized_role = 'employee'
                elif record.authorized_person_id.company_type == 'company':
                    record.authorized_role = 'company_rep'
                else:
                    record.authorized_role = False
            else:
                record.authorized_role = False

    @api.model
    def _send_expiration_notification(self):
        records = self.search([('end_date', '=', fields.Date.today() + timedelta(days=7))])
        for record in records:
            message = _("The authorization/agency %s will expire in 7 days.") % (record.name)
            record.message_post(body=message)

    @api.model
    def _create_warning_notification(self, authorization):
        notification_message = _(
            "Upcoming expiration for %s: Authorization/Agency %s for %s will expire on %s."
        ) % (
            authorization.name,
            authorization.authorization_type,
            authorization.partner_id.name,
            authorization.end_date.strftime('%Y-%m-%d')
        )

        self.env['mail.message'].create({
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_note').id,
            'body': notification_message,
            'model': 'legal.authorization.agency',
            'res_id': authorization.id,
            'partner_ids': [(6, 0, self.env.user.partner_id.ids)]
        })

    @api.model
    def _check_and_notify_expiring_authorizations(self):
        today = fields.Date.today()
        expiring_authorizations = self.search([
            ('end_date', '=', today + timedelta(days=7)),
            ('document_status', '!=', 'cancelled')
        ])
        for authorization in expiring_authorizations:
            self._create_warning_notification(authorization)