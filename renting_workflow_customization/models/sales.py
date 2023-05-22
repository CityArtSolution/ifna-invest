# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"
    state = fields.Selection([
        ('draft_q', 'Draft Quotation'),
        ('ff_review', 'Facility & Finance Review'),
        ('ceo', 'CEO Approve'),
        ('draft', 'Issued Quotation'),
        ('sent', 'Quotation Sent'),
        ('initial_contract', 'Initial Contract'),
        ('ffl_review', 'Facility & Finance & Legal Review'),
        ('draft_contract', 'Draft Contract'),
        ('upload_doc', 'Upload Document'),
        ('view_all_ceo_approve', 'View All Doc & CEO Approve'),
        ('ejar_upload', 'Ejar Contract Upload'),
        ('finance_review', 'Finance Review'),
        ('sale', 'CEO Approval'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft_q')