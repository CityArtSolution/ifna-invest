# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, MissingError


class LegalExecutionRequest(models.Model):
    _name = 'legal.execution.request'
    _description = 'Legal Execution Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    name = fields.Char(string="Request Number", required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    case_id = fields.Many2one('legal.case', 'Case', tracking=True)
    plaintiff_id = fields.Many2one("res.partner", "Plaintiff", domain=[('is_legal_plaintiff', '=', True)], related="case_id.plaintiff_id", tracking=True)
    partner_id = fields.Many2one('res.partner', string="Defendant", domain=[('is_legal_defendant', '=', True)], related="case_id.partner_id", required=True)
    execution_amount = fields.Float(string="Execution Amount", compute="_compute_execution_amount", store=True, readonly=False)
    court_id = fields.Many2one('legal.court', string="Court", related="case_id.court_id", tracking=True)
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
    state = fields.Selection([
        ('paid', 'Paid'),
        ('not_paid', 'Un Paid'),
    ], string='State')

    account_journal_count = fields.Integer(compute="_compute_account_journal_count")
    journal_id = fields.Many2one('account.journal', 'Account Journal', domain=[('type', 'in', ('bank', 'cash'))], tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('legal.execution.request') or 'New'
            vals['name'] = seq
        record = super(LegalExecutionRequest, self).create(vals)
        if record.state == 'paid':
            self._send_notification(record)
        return record

    def write(self, vals):
        res = super(LegalExecutionRequest, self).write(vals)
        for record in self:
            if 'state' in vals and record.state == 'paid':
                self._send_notification(record)
        return res

    def _send_notification(self, record):
        message_body = (
            f"Amount received {record.execution_amount} {record.currency_id.symbol}for Execution Number {record.name} for the court account."
        )

        group = self.env.ref('legal_affairs_management.group_account_financial_manager')
        partners = self.env['res.users'].search([('groups_id', 'in', group.id)]).mapped('partner_id')

        self.env['mail.message'].create({
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_note').id,
            'body': message_body,
            'model': 'legal.execution.request',
            'res_id': record.id,
            'partner_ids': [(6, 0, partners.ids)]
        })

    @api.onchange('execution_amount')
    def _onchange_execution_amount(self):
        if self.execution_amount > 100000:
            return {
                'warning': {
                    'title': _('High Amount Warning'),
                    'message': _('The execution amount is very high. Please double-check.'),
                }
            }

    def action_create_journal_entries(self):
        if self.state != 'paid':
            raise UserError(_('The execution request state must be paid.'))

        partner_account = self.partner_id.property_account_receivable_id
        case_account = self.case_id.case_type_id.account_id

        if not partner_account or not case_account:
            raise UserError(_('Partner or Case account is not configured properly.'))

        debit_amount = 100
        credit_amount = 100

        default_line_ids = [
            (0, 0, {
                'account_id': partner_account.id,
                'partner_id': self.partner_id.id,
                'debit': debit_amount,
                'credit': 0.0,
                'name': _('Account Receivable Entry')
            }),
            (0, 0, {
                'account_id': case_account.id,
                'partner_id': self.partner_id.id,
                'debit': 0.0,
                'credit': credit_amount,
                'name': _('Case Account Entry')
            }),
        ]

        journal_entry = self.env['account.move'].create({
            'move_type': 'entry',
            'ref': self.name,
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'line_ids': default_line_ids,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Journal Entry'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': journal_entry.id,
            'target': 'current',
        }

    @api.depends('partner_id', 'name')
    def _compute_account_journal_count(self):
        for rec in self:
            journal_counts = self.env['account.move'].sudo().search_count([
                ('move_type', '=', 'entry'),
                ('ref', '=', self.name),
                ('partner_id', '=', self.partner_id.id),
            ])
            rec.account_journal_count = journal_counts

    def action_view_journal_entries(self):
        self.ensure_one()
        if self.account_journal_count > 0:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Journal Entries'),
                'res_model': 'account.move',
                'view_mode': 'tree,kanban,form',
                'domain': [
                    ('move_type', '=', 'entry'),
                    ('ref', '=', self.name),
                    ('partner_id', '=', self.partner_id.id),
                ],
            }
        else:
            return {'type': 'ir.actions.act_window_close'}

    @api.depends()
    def _compute_execution_amount(self):
        for rec in self:
            if rec.partner_id:
                rec.execution_amount = rec.partner_id.total_overdue_amount
            else:
                rec.execution_amount = 0.0
