# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date


class LegalCaseMatters(models.Model):
    _name = 'legal.case'
    _description = 'Legal Case & Matters'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    name = fields.Char(string="Case Number", required=True, tracking=True)
    case_type_id = fields.Many2one('legal.case.type', string="Case Type", tracking=True)

    plaintiff_id = fields.Many2one("res.partner", "Plaintiff", domain=[('is_legal_plaintiff', '=', True)], tracking=True)
    partner_id = fields.Many2one('res.partner', 'Defendant', domain=[('is_legal_defendant', '=', True)], tracking=True)

    lawyer_id = fields.Many2one('res.partner', string="Lawyer", domain=[('is_legal_lawyer', '=', True)], tracking=True)
    legal_field = fields.Char(string="Legal Field", related="lawyer_id.lawyer_law_area", tracking=True)

    judge_id = fields.Many2one('res.partner', string="Judge", domain=[('is_legal_judge', '=', True)],
                               tracking=True)
    case_date = fields.Date(string="Date Filed", tracking=True)
    case_status = fields.Selection([('open', 'Open'), ('closed', 'Closed')], string="Case Status", tracking=True)
    claim_amount = fields.Float(string="Claim Amount", compute="_compute_claim_amount", store=True, readonly=False, tracking=True, help="Sum of total overdue amount defendant invoices")
    judgment_amount = fields.Float(string="Judgment Amount", tracking=True)
    court_id = fields.Many2one('legal.court', string="Court", tracking=True)
    court_level_id = fields.Many2one('legal.court.level', related="court_id.court_level_id", string="Court Level", tracking=True)

    expected_collection_date = fields.Date("Expected Collection", tracking=True)

    attachment_ids = fields.Many2many('ir.attachment', string="Attachments", tracking=True)

    trail_ids = fields.One2many('legal.trial', 'case_id', string='Trails', tracking=True)
    legal_trail_count = fields.Integer(compute='_compute_legal_trail_count')

    execution_request_count = fields.Integer(compute='_compute_execution_request_count')

    account_move_ids = fields.One2many('account.move', 'case_id', string='Invoices', tracking=True)
    account_move_count = fields.Integer(compute='_compute_account_move_count')

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'Name already exists!')
    ]

    @api.depends('partner_id')
    def _compute_claim_amount(self):
        for rec in self:
            if rec.partner_id:
                rec.claim_amount = rec.partner_id.total_overdue_amount
            else:
                rec.claim_amount = 0.0

    @api.depends('trail_ids')
    def _compute_legal_trail_count(self):
        for rec in self:
            rec.legal_trail_count = self.env['legal.trial'].search_count([
                ('case_id', '=', rec.id),
            ])

    def action_view_legal_trail(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Legal Trail'),
            'res_model': 'legal.trial',
            'view_mode': 'tree,form',
            'domain': [
                ('case_id', '=', self.id),
            ],
            'context': {'default_case_id': self.id, 'default_partner_id': self.partner_id.id}
        }

    def action_create_legal_trail(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Trail'),
            'view_mode': 'form',
            'res_model': 'legal.trial',
            'target': 'self',
            'context': {'default_case_id': self.id, 'default_partner_id': self.partner_id.id}
        }

    @api.depends('partner_id')
    def _compute_execution_request_count(self):
        for rec in self:
            execution_request_counts = self.env['legal.execution.request'].sudo().search_count(
                [('case_id', '=', self.id), ('partner_id', '=', self.partner_id.id)])
            rec.execution_request_count = execution_request_counts

    def action_view_execution_request(self):
        execution_request = self.env['legal.execution.request'].sudo().search(
            [('case_id', '=', self.id), ('partner_id', '=', self.partner_id.id)], limit=1)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Journal Entry'),
            'res_model': 'legal.execution.request',
            'view_mode': 'form',
            'res_id': execution_request.id,
            'target': 'current',
        }

    def action_create_execution_request(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Execution Request'),
            'view_mode': 'form',
            'res_model': 'legal.execution.request',
            'target': 'self',
            'context': {'default_case_id': self.id, 'default_partner_id': self.partner_id.id}
        }

    @api.depends('partner_id')
    def _compute_account_move_count(self):
        for rec in self:
            account_move_counts = self.env['account.move'].sudo().search_count(
                [('case_id', '=', self.id), ('partner_id', '=', self.partner_id.id), ('move_type', '=', 'out_invoice')])
            rec.account_move_count = account_move_counts

    def action_view_account_move_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Defendant Invoices'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('is_legal_invoice', '=', True), ('case_id', '=', self.id), ('partner_id', '=', self.partner_id.id),
                       ('move_type', '=', 'out_invoice')],
            'context': {'default_is_legal_invoice': True, 'default_case_id': self.id, 'default_partner_id': self.partner_id.id,
                        'default_move_type': 'out_invoice'},
            'target': 'current',
        }

    def action_create_account_move_invoices(self):
        # Create the account move (invoice)
        account_move = self.env['account.move'].sudo().create({
            'partner_id': self.partner_id.id,
            'case_id': self.id,
            'move_type': 'out_invoice',
            'invoice_date': date.today(),
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.env.ref('legal_affairs_management.legal_product_product_case_data').id,
                    'name': self.env.ref('legal_affairs_management.legal_product_product_case_data').name,
                    'quantity': 1,
                    'price_unit': self.claim_amount,
                    'tax_ids': False,
                })
            ]
        })

        # Return action to open the created invoice in form view
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Defendant Invoices'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': account_move.id,
            'target': 'self',
        }

