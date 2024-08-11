# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class LegalResPartner(models.Model):
    _inherit = "res.partner"

    is_legal_client = fields.Boolean(string="Client")
    is_legal_defendant = fields.Boolean(string="Defendant")

    total_overdue_amount = fields.Monetary(string="Total Overdue Amount", compute='_compute_total_overdue_amount', store=True)
    overdue_invoice_count = fields.Integer(compute='_compute_overdue_invoice_count')

    @api.depends('invoice_ids')
    def _compute_total_overdue_amount(self):
        for partner in self:
            overdue_invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date_due', '<', fields.Date.today()),
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'paid'),
            ])
            partner.total_overdue_amount = sum(invoice.amount_total for invoice in overdue_invoices)

    @api.depends('invoice_ids')
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
