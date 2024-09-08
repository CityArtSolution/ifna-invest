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
    execution_amount = fields.Float(string="Execution Amount", compute="_compute_execution_amount", store=True, readonly=False, tracking=True)
    is_remaining_amount = fields.Boolean()
    remaining_amount = fields.Float(string="Remaining Amount", tracking=True)
    account_id = fields.Many2one("account.account", "Remaining Account", tracking=True)
    court_id = fields.Many2one('legal.court', string="Court", related="case_id.court_id", tracking=True)
    execution_number = fields.Char(string="Execution Number", tracking=True)
    document_status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('submitted', 'Submitted'),
    ], string="Document Status", default='draft', tracking=True)

    notes = fields.Text(string="Notes", tracking=True)
    attachment = fields.Binary(string="Attachment", tracking=True)
    attachment_filename = fields.Char(string="Attachment Filename", tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id, tracking=True)
    state = fields.Selection([
        ('paid', 'Paid'),
        ('not_paid', 'Un Paid'),
        ('other', 'Other'),
    ], string='State', tracking=True)

    account_journal_count = fields.Integer(compute="_compute_account_journal_count")
    journal_id = fields.Many2one('account.journal', 'Account Journal', domain=[('type', 'in', ('bank', 'cash'))], tracking=True)

    account_payment_ids = fields.One2many('account.payment', 'case_id', string='Payments', tracking=True)
    account_payment_count = fields.Integer(compute='_compute_account_payment_count')
    operating_unit_id = fields.Many2one('operating.unit', string="Operating Unit")

    total_required = fields.Float("Total Amount", compute="_compute_total_required", store=True, tracking=True)
    total_payment = fields.Float("Payments Amount", compute="_compute_total_payment", store=True, tracking=True)
    total_residual = fields.Float("Residual Amount", compute="_compute_total_residual", store=True, tracking=True)

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
            raise UserError(_('The execution request state must be "paid".'))

        # Fetching necessary accounts
        partner_account = self.partner_id.property_account_receivable_id
        case_account = self.case_id.case_type_id.account_id
        remaining_account = self.account_id

        # Ensuring required accounts are set
        if not partner_account:
            raise UserError(_('The partner does not have a receivable account configured.'))
        if not case_account:
            raise UserError(_('The case type does not have an account configured.'))

        # Calculate amounts
        debit_amount_1 = self.execution_amount
        debit_amount_2 = self.remaining_amount if self.remaining_amount else 0.0
        credit_amount = self.execution_amount + debit_amount_2

        # Prepare journal entry lines
        line_ids = [
            (0, 0, {
                'account_id': partner_account.id,
                'partner_id': self.partner_id.id,
                'debit': debit_amount_1,
                'credit': 0.0,
                'name': _('Account Receivable Entry'),
            }),
            (0, 0, {
                'account_id': case_account.id,
                'partner_id': self.partner_id.id,
                'debit': 0.0,
                'credit': credit_amount,
                'name': _('Case Account Entry'),
            }),
        ]

        # Include remaining amount entry if applicable
        if debit_amount_2 > 0:
            line_ids.append(
                (0, 0, {
                    'account_id': remaining_account.id,
                    'partner_id': self.partner_id.id,
                    'debit': debit_amount_2,
                    'credit': 0.0,
                    'name': _('Remaining Account Entry'),
                })
            )

        # Create the journal entry
        journal_entry = self.env['account.move'].create({
            'move_type': 'entry',
            'ref': self.name,
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'line_ids': line_ids,
        })

        # Return action to open the created journal entry
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

    @api.depends('case_id')
    def _compute_execution_amount(self):
        for rec in self:
            if rec.case_id:
                rec.execution_amount = rec.case_id.claim_amount
            else:
                rec.execution_amount = 0.0

    @api.onchange('execution_amount')
    def _onchange_execution_amount(self):
        for rec in self:
            if rec.execution_amount and rec.case_id:
                claim_amount = rec.case_id.claim_amount
                if rec.execution_amount < claim_amount:
                    rec.is_remaining_amount = True
                    difference = rec.remaining_amount =  claim_amount - rec.execution_amount
                    currency_symbol = rec.currency_id.symbol

                    return {
                        'warning': {
                            'title': _("Warning"),
                            'message': _(
                                "The Execution Amount is less than the Claim Amount. The difference is: %s %.2f") % (
                                       currency_symbol, difference),
                        }
                    }
                else:
                    rec.is_remaining_amount = False
            else:
                rec.is_remaining_amount = False

    @api.depends('case_id')
    def _compute_account_payment_count(self):
        for rec in self:
            account_payment_counts = self.env['account.payment'].sudo().search_count([('case_id', '=', self.case_id.id)])
            rec.account_payment_count = account_payment_counts

    def action_view_account_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Account Payments'),
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('is_legal_payment', '=', True), ('case_id', '=', self.case_id.id)],
            'context': {'default_is_legal_payment': True, 'default_case_id': self.case_id.id,
                        'default_partner_id': self.partner_id.id,
                        'default_amount': self.execution_amount, 'default_ref': str("PAY#" + self.name)},
            'target': 'current',
        }

    def action_create_account_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Account Payment'),
            'view_mode': 'form',
            'res_model': 'account.payment',
            'context': {'default_is_legal_payment': True, 'default_case_id': self.case_id.id,
                        'default_partner_id': self.partner_id.id,
                        'default_amount': self.execution_amount, 'default_ref': str("PAY#" + self.name)},
            'target': 'self',
        }

    @api.depends('case_id')
    def _compute_total_required(self):
        for rec in self:
            if rec.case_id:
                rec.total_required = rec.case_id.claim_amount
            else:
                rec.total_required = 0.0

    @api.depends('account_payment_ids')
    def _compute_total_payment(self):
        for rec in self:
            if rec.case_id:
                payments = rec.account_payment_ids.filtered(lambda p: p.case_id == rec.case_id)
                rec.total_payment = sum(payment.amount for payment in payments)
            else:
                rec.total_payment = 0.0

    @api.depends('total_required', 'total_payment')
    def _compute_total_residual(self):
        for rec in self:
            if rec.total_required:
                rec.total_residual = rec.total_required - rec.total_payment
            else:
                rec.total_residual = 0.0

