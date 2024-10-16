# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta


class LegalTrial(models.Model):
    _name = 'legal.trial'
    _description = 'Legal Trial'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'case_id'

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    case_id = fields.Many2one('legal.case', string="Case Number", tracking=True, required=True)
    court_id = fields.Many2one('legal.court', string="Court", related="case_id.court_id", tracking=True)

    partner_id = fields.Many2one('res.partner', string="Defendant", related="case_id.partner_id", tracking=True)
    lawyer_id = fields.Many2one('res.partner', string="Lawyer", related="case_id.lawyer_id", tracking=True)

    expected_collection_date = fields.Date("Expected Collection", compute="_compute_expected_collection_date", store=True, readonly=False, tracking=True)

    trial_date = fields.Datetime(string="Trial Date", tracking=True)
    trail_details = fields.Text(string="Trial Details", tracking=True)
    trial_state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string="Trial State", default='draft', tracking=True)
    attachment = fields.Binary(string="Attachment", tracking=True)
    attachment_filename = fields.Char(string="Attachment Filename", tracking=True)
    notes = fields.Text(string="Notes", tracking=True)
    reminder_sent = fields.Boolean(string="Reminder Sent", default=False)

    @api.depends('case_id')
    def _compute_expected_collection_date(self):
        for rec in self:
            if rec.case_id:
                rec.expected_collection_date = rec.case_id.expected_collection_date

    @api.model
    def send_trial_reminders(self):
        today = datetime.now()
        one_week_from_today = today + timedelta(days=7)
        one_week_from_today_start = one_week_from_today.replace(hour=0, minute=0, second=0, microsecond=0)
        one_week_from_today_end = one_week_from_today.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Find trials that are one week away and haven't been reminded
        trials_to_remind = self.search([
            ('trial_date', '>=', one_week_from_today_start),
            ('trial_date', '<=', one_week_from_today_end),
            ('reminder_sent', '=', False)
        ])

        for trial in trials_to_remind:
            # Send reminder email or message
            self._send_reminder(trial)

            self._create_warning_notification(trial)

            # Update reminder_sent field
            trial.reminder_sent = True

    def _send_reminder(self, trial):
        subject = _('Reminder: Upcoming Trial')
        body = _(
            "Dear %(user_name)s,\n\n"
            "This is a reminder that the trial for case %(case_name)s is scheduled for %(trial_date)s.\n\n"
            "Best regards,\nYour Legal Affairs Team"
        ) % {
            'user_name': self.env.user.partner_id.name,
            'case_name': trial.case_id.name,
            'trial_date': trial.trial_date.strftime('%Y-%m-%d %H:%M:%S')
        }

        mail_values = {
            'subject': subject,
            'body_html': body,
            'email_to': self.env.user.partner_id.email,
        }
        self.env['mail.mail'].create(mail_values).send()

    def _create_warning_notification(self, trial):
        notification_message = _(
            "Upcoming trial for case %(case_name)s is scheduled for %(trial_date)s."
        ) % {
            'case_name': trial.case_id.name,
            'trial_date': trial.trial_date.strftime('%Y-%m-%d %H:%M:%S')
        }

        self.env['mail.message'].create({
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_note').id,
            'body': notification_message,
            'model': 'legal.trial',
            'res_id': trial.id,
            'partner_ids': [(6, 0, self.env.user.partner_id.ids)]
        })