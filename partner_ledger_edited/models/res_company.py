# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    excel_format = fields.Char(string='Excel format', default='_ * #,##0.00_) ;_ * - #,##0.00_) ;_ * "-"??_) ;_ @_ ',
                               required=True)

    financial_year = fields.Selection([
        ('april_march', '1 April to 31 March'),
        ('july_june', '1 july to 30 June'),
        ('january_december', '1 Jan to 31 Dec')
    ], string='Financial Year', default='january_december', required=True)

    date_range = fields.Selection(
        [('today', 'Today'),
         ('this_week', 'This Week'),
         ('this_month', 'This Month'),
         ('this_quarter', 'This Quarter'),
         ('this_financial_year', 'This financial Year'),
         ('yesterday', 'Yesterday'),
         ('last_week', 'Last Week'),
         ('last_month', 'Last Month'),
         ('last_quarter', 'Last Quarter'),
         ('last_financial_year', 'Last Financial Year')],
        string='Default Date Range', default='this_financial_year', required=True)


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    excel_format = fields.Char(string='Excel format', default='_ * #,##0.00_) ;_ * - #,##0.00_) ;_ * "-"??_) ;_ @_ ',
                               required=True)

    financial_year = fields.Selection([
        ('april_march', '1 April to 31 March'),
        ('july_june', '1 july to 30 June'),
        ('january_december', '1 Jan to 31 Dec')
    ], string='Financial Year', default='january_december', required=True)
