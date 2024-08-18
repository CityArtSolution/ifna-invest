# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta


class LegalTrial(models.Model):
    _name = 'legal.trial'
    _description = 'Legal Trial'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'case_id'

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    case_id = fields.Many2one('legal.case', string="Case Number", tracking=True)
    court_id = fields.Many2one('legal.court', string="Court Name", related="case_id.court_id", tracking=True)

    partner_id = fields.Many2one('res.partner', string="Defendant", related="case_id.partner_id", tracking=True)
    lawyer_id = fields.Many2one('res.partner', string="Lawyer Name", related="case_id.lawyer_id", tracking=True)

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
        body = _(f"Dear {self.env.user.partner_id.name},\n\n" \
                 f"This is a reminder that the trial for case {trial.case_id.name} is scheduled for {trial.trial_date.strftime('%Y-%m-%d %H:%M:%S')}.\n\n" \
                 f"Best regards,\nYour Legal Affairs Team")

        mail_values = {
            'subject': subject,
            'body_html': body,
            'email_to': self.env.user.partner_id.email,
        }
        self.env['mail.mail'].send().create(mail_values)

    def _create_warning_notification(self, trial):
        notification_message = f"Upcoming trial for case {trial.case_id.name} is scheduled for {trial.trial_date.strftime('%Y-%m-%d %H:%M:%S')}."

        self.env['mail.message'].create({
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_note').id,
            'body': notification_message,
            'model': 'legal.trial',
            'res_id': trial.id,
            'partner_ids': [(6, 0, self.env.user.partner_id.ids)]
        })
