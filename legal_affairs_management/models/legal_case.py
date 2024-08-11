# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class LegalCaseMatters(models.Model):
    _name = 'legal.case'
    _description = 'Legal Case & Matters'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    name = fields.Char(string="Case Number", required=True, tracking=True)
    case_type_id = fields.Many2one('legal.case.type', string="Case Type", tracking=True)

    plaintiff = fields.Char(string="Plaintiff", tracking=True)
    partner_id = fields.Many2one('res.partner', 'Defendant', domain=[('is_legal_defendant', '=', True)], tracking=True)

    lawyer_id = fields.Many2one('legal.lawyer', string="Lawyer", tracking=True)
    legal_field = fields.Char(string="Legal Field", tracking=True, related="lawyer_id.law_area")

    judge_id = fields.Many2one('legal.judge', string="Judge Name", tracking=True)
    case_date = fields.Date(string="Date Filed", tracking=True)
    claim_amount = fields.Float(string="Claim Amount", tracking=True)
    court_id = fields.Many2one('legal.court', string="Court Name", tracking=True)

    attachment_ids = fields.Many2many('ir.attachment', string="Attachments", tracking=True)

    trail_ids = fields.One2many('legal.trial', 'case_id', string='Trails', tracking=True)
    legal_trail_count = fields.Integer(compute='_compute_legal_trail_count')

    court_level = fields.Selection([('primary', 'Primary Court'), ('appeal', 'Appeal Court')], string="Court Level",
                                   tracking=True)
    case_status = fields.Selection([('open', 'Open'), ('closed', 'Closed')], string="Case Status", tracking=True)

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