# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class LegalResPartner(models.Model):
    _inherit = "res.partner"

    is_legal_plaintiff = fields.Boolean(string="Plaintiff", tracking=True)
    is_legal_defendant = fields.Boolean(string="Defendant", tracking=True)
    is_legal_lawyer = fields.Boolean(string="Lawyer", tracking=True)
    is_legal_judge = fields.Boolean(string="Judge", tracking=True)
    is_legal_authorized = fields.Boolean(string="Authorized", tracking=True)
    is_main_view = fields.Boolean(compute="_compute_is_main_view")
    show_legal_group = fields.Boolean(compute='_compute_show_legal_group')

    lawyer_law_area = fields.Char(string="Law Area", tracking=True)

    total_overdue_amount = fields.Float(string="Total Overdue Amount", compute='_compute_total_overdue_amount',
                                           store=True)
    overdue_invoice_count = fields.Integer(compute='_compute_overdue_invoice_count')

    @api.model
    def _compute_total_overdue_amount(self):
        for partner in self:
            overdue_invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date_due', '<=', fields.Date.today()),
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'paid'),
            ])
            partner.total_overdue_amount = sum(invoice.amount_total for invoice in overdue_invoices)

    @api.model
    def _compute_overdue_invoice_count(self):
        for partner in self:
            partner.overdue_invoice_count = self.env['account.move'].search_count([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date_due', '<', fields.Date.today()),
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'paid'),
            ])

    def action_view_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Overdue Invoices'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [
                ('partner_id', '=', self.id),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date_due', '<', fields.Date.today()),
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'paid'),
            ],
            'context': {'create': False}
        }

    def action_view_latest_invoice_pdf(self):
        latest_invoice = self.env['account.move'].search([
            ('partner_id', '=', self.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ], order='invoice_date desc', limit=1)

        if latest_invoice:
            return self.env.ref('account.account_invoices').report_action(latest_invoice)
        else:
            return {'type': 'ir.actions.act_window_close'}

    @api.depends('is_legal_defendant', 'is_legal_lawyer', 'is_legal_judge',
                 'is_legal_authorized')
    def _compute_show_legal_group(self):
        for record in self:
            record.show_legal_group = (
                self.env.context.get('default_is_legal_defendant', False) or
                self.env.context.get('default_is_legal_lawyer', False) or
                self.env.context.get('default_is_legal_judge', False) or
                self.env.context.get('default_is_legal_authorized', False)
            )

    @api.depends("is_company")
    def _compute_is_main_view(self):
        for record in self:
            record.is_main_view = (
                self.env.context.get('default_is_company', False)
            )
