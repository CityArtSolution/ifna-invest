import calendar
import io
import json
import logging
import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import date_utils

import io
import xlsxwriter
from collections import defaultdict
import datetime
from string import ascii_uppercase
from odoo import http, fields, models, _
from odoo.http import request

DATE_DICT = {
    '%m/%d/%Y': 'mm/dd/yyyy',
    '%Y/%m/%d': 'yyyy/mm/dd',
    '%m/%d/%y': 'mm/dd/yy',
    '%d/%m/%Y': 'dd/mm/yyyy',
    '%d/%m/%y': 'dd/mm/yy',
    '%d-%m-%Y': 'dd-mm-yyyy',
    '%d-%m-%y': 'dd-mm-yy',
    '%m-%d-%Y': 'mm-dd-yyyy',
    '%m-%d-%y': 'mm-dd-yy',
    '%Y-%m-%d': 'yyyy-mm-dd',
    '%f/%e/%Y': 'm/d/yyyy',
    '%f/%e/%y': 'm/d/yy',
    '%e/%f/%Y': 'd/m/yyyy',
    '%e/%f/%y': 'd/m/yy',
    '%f-%e-%Y': 'm-d-yyyy',
    '%f-%e-%y': 'm-d-yy',
    '%e-%f-%Y': 'd-m-yyyy',
    '%e-%f-%y': 'd-m-yy'
}

FETCH_RANGE = 2000


class InsPartnerLedger(models.TransientModel):
    _name = "ins.partner.ledger.edited"
    try:
        _inherit = 'report.report_xlsx.abstract'
    except ImportError:
        _logger.debug('Cannot find report_xlsx module for version 11')

    # @api.onchange('date_range', 'financial_year')
    # def onchange_date_range(self):
    #     if self.date_range:
    #         date = datetime.today()
    #         if self.date_range == 'today':
    #             self.date_from = date.strftime("%Y-%m-%d")
    #             self.date_to = date.strftime("%Y-%m-%d")
    #         if self.date_range == 'this_week':
    #             day_today = date - timedelta(days=date.weekday())
    #             self.date_from = (day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
    #             self.date_to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")
    #         if self.date_range == 'this_month':
    #             self.date_from = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
    #             self.date_to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
    #         if self.date_range == 'this_quarter':
    #             if int((date.month - 1) / 3) == 0:  # First quarter
    #                 self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
    #                 self.date_to = datetime(date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
    #             if int((date.month - 1) / 3) == 1:  # Second quarter
    #                 self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
    #                 self.date_to = datetime(date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
    #             if int((date.month - 1) / 3) == 2:  # Third quarter
    #                 self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
    #                 self.date_to = datetime(date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
    #             if int((date.month - 1) / 3) == 3:  # Fourth quarter
    #                 self.date_from = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
    #                 self.date_to = datetime(date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
    #         if self.date_range == 'this_financial_year':
    #             if self.financial_year == 'january_december':
    #                 self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
    #                 self.date_to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
    #             if self.financial_year == 'april_march':
    #                 if date.month < 4:
    #                     self.date_from = datetime(date.year - 1, 4, 1).strftime("%Y-%m-%d")
    #                     self.date_to = datetime(date.year, 3, 31).strftime("%Y-%m-%d")
    #                 else:
    #                     self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
    #                     self.date_to = datetime(date.year + 1, 3, 31).strftime("%Y-%m-%d")
    #             if self.financial_year == 'july_june':
    #                 if date.month < 7:
    #                     self.date_from = datetime(date.year - 1, 7, 1).strftime("%Y-%m-%d")
    #                     self.date_to = datetime(date.year, 6, 30).strftime("%Y-%m-%d")
    #                 else:
    #                     self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
    #                     self.date_to = datetime(date.year + 1, 6, 30).strftime("%Y-%m-%d")
    #         date = (datetime.now() - relativedelta(days=1))
    #         if self.date_range == 'yesterday':
    #             self.date_from = date.strftime("%Y-%m-%d")
    #             self.date_to = date.strftime("%Y-%m-%d")
    #         date = (datetime.now() - relativedelta(days=7))
    #         if self.date_range == 'last_week':
    #             day_today = date - timedelta(days=date.weekday())
    #             self.date_from = (day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
    #             self.date_to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")
    #         date = (datetime.now() - relativedelta(months=1))
    #         if self.date_range == 'last_month':
    #             self.date_from = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
    #             self.date_to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
    #         date = (datetime.now() - relativedelta(months=3))
    #         if self.date_range == 'last_quarter':
    #             if int((date.month - 1) / 3) == 0:  # First quarter
    #                 self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
    #                 self.date_to = datetime(date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
    #             if int((date.month - 1) / 3) == 1:  # Second quarter
    #                 self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
    #                 self.date_to = datetime(date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
    #             if int((date.month - 1) / 3) == 2:  # Third quarter
    #                 self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
    #                 self.date_to = datetime(date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
    #             if int((date.month - 1) / 3) == 3:  # Fourth quarter
    #                 self.date_from = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
    #                 self.date_to = datetime(date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
    #         date = (datetime.now() - relativedelta(years=1))
    #         if self.date_range == 'last_financial_year':
    #             if self.financial_year == 'january_december':
    #                 self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
    #                 self.date_to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
    #             if self.financial_year == 'april_march':
    #                 if date.month < 4:
    #                     self.date_from = datetime(date.year - 1, 4, 1).strftime("%Y-%m-%d")
    #                     self.date_to = datetime(date.year, 3, 31).strftime("%Y-%m-%d")
    #                 else:
    #                     self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
    #                     self.date_to = datetime(date.year + 1, 3, 31).strftime("%Y-%m-%d")
    #             if self.financial_year == 'july_june':
    #                 if date.month < 7:
    #                     self.date_from = datetime(date.year - 1, 7, 1).strftime("%Y-%m-%d")
    #                     self.date_to = datetime(date.year, 6, 30).strftime("%Y-%m-%d")
    #                 else:
    #                     self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
    #                     self.date_to = datetime(date.year + 1, 6, 30).strftime("%Y-%m-%d")

    # @api.model
    # def _get_default_date_range(self):
    #     return self.env.company.date_range
    def get_accounts(self):
        return self.env['account.account'].search([])
    
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, 'Partner Ledger'))
        return res

    financial_year = fields.Selection(
        [('april_march', '1 April to 31 March'),
         ('july_june', '1 july to 30 June'),
         ('january_december', '1 Jan to 31 Dec')],
        string='Financial Year', default=lambda self: self.env.company.financial_year, required=True)

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
        string='Date Range'
    )
    target_moves = fields.Selection(
        [('all_entries', 'All entries'),
         ('posted_only', 'Posted Only')], string='Target Moves',
        default='posted_only', required=True
    )
    display_accounts = fields.Selection(
        [('all', 'All'),
         ('balance_not_zero', 'With balance not equal to zero')], string='Display accounts',
        default='balance_not_zero', required=True
    )
    balance_less_than_zero = fields.Boolean(
        string='With balance less than zero')
    balance_greater_than_zero = fields.Boolean(
        string='With balance greater than zero')
    type = fields.Selection(
        [('receivable', 'Receivable Only'),
         ('payable', 'Payable only')],
        string='Account Type', required=False
    )
    initial_balance = fields.Boolean(
        string='Include Initial Balance', default=True
    )
    reconciled = fields.Selection([('reconciled', 'Reconciled Only'),
                                   ('unreconciled', 'Unreconciled Only')],
                                  string='Reconcile Type')
    date_from = fields.Date(
        string='Start date',
    )
    date_to = fields.Date(
        string='End date',
    )
    account_ids = fields.Many2many(
        'account.account', string='Accounts', default=get_accounts)
    journal_ids = fields.Many2many(
        'account.journal', string='Journals',
    )
    partner_ids = fields.Many2many(
        'res.partner', string='Partners'
    )
    units_ids = fields.Many2many(
        'product.product', string='Units'
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company
    )
    include_details = fields.Boolean(
        string='Include Details', default=True
    )
    partner_category_ids = fields.Many2many(
        'res.partner.category', string='Partner Tag',
    )

    @api.model
    def create(self, vals):
        ret = super(InsPartnerLedger, self).create(vals)
        return ret

    def validate_data(self):
        if self.date_from > self.date_to:
            raise ValidationError(
                _('"Date from" must be less than or equal to "Date to"'))
        return True

    def process_filters(self):
        ''' To show on report headers'''

        data = self.get_filters(default_filters={})

        filters = {}
        if data.get('display_accounts') == 'balance_not_zero':
            filters['display_accounts'] = 'With balance not Zero'
        if data.get('balance_less_than_zero'):
            filters['display_accounts'] = 'With balance less than Zero'
        if data.get('balance_greater_than_zero'):
            filters['display_accounts'] = 'With balance greater than Zero'
        else:
            filters['display_accounts'] = 'All'
        if data.get('journal_ids', []):
            filters['journals'] = self.env['account.journal'].browse(
                data.get('journal_ids', [])).mapped('code')
        else:
            filters['journals'] = ['All']
        if data.get('account_ids', []):
            filters['accounts'] = self.env['account.account'].browse(
                data.get('account_ids', [])).mapped('code')
        else:
            filters['accounts'] = ['All']

        if data.get('partner_ids', []):
            filters['partners'] = self.env['res.partner'].browse(
                data.get('partner_ids', [])).mapped('name')
        else:
            filters['partners'] = ['All']

        if data.get('units_ids', []):
            filters['partners'] = self.env['res.partner'].browse(
                data.get('units_ids', [])).mapped('name')
        else:
            filters['units_ids'] = ['All']

        if data.get('partner_category_ids', []):
            filters['categories'] = self.env['res.partner.category'].browse(
                data.get('partner_category_ids', [])).mapped('name')
        else:
            filters['categories'] = ['All']

        if data.get('target_moves') == 'all_entries':
            filters['target_moves'] = 'All Entries'
        else:
            filters['target_moves'] = 'Posted Only'

        if data.get('date_from', False):
            filters['date_from'] = data.get('date_from')
        if data.get('date_to', False):
            filters['date_to'] = data.get('date_to')

        if data.get('initial_balance'):
            filters['initial_balance'] = 'Yes'
        else:
            filters['initial_balance'] = 'No'

        filters['reconciled'] = '-'
        if data.get('reconciled') == 'reconciled':
            filters['reconciled'] = 'Yes'
        if data.get('reconciled') == 'unreconciled':
            filters['reconciled'] = 'No'

        if data.get('company_id'):
            filters['company_id'] = data.get('company_id')
        else:
            filters['company_id'] = ''

        if data.get('include_details'):
            filters['include_details'] = True
        else:
            filters['include_details'] = False

        filters['journals_list'] = data.get('journals_list')
        filters['accounts_list'] = data.get('accounts_list')
        filters['partners_list'] = data.get('partners_list')
        filters['category_list'] = data.get('category_list')
        filters['company_name'] = data.get('company_name')

        return filters

    def build_where_clause(self, data=False):
        if not data:
            data = self.get_filters(default_filters={})

        if data:

            WHERE = '(1=1)'

            type = ('receivable', 'payable')
            if self.type:
                type = tuple([self.type, 'none'])

            WHERE += ' AND ty.type IN %s' % str(type)

            if data.get('reconciled') == 'reconciled':
                WHERE += ' AND l.amount_residual = 0'
            if data.get('reconciled') == 'unreconciled':
                WHERE += ' AND l.amount_residual != 0'

            if data.get('journal_ids', []):
                WHERE += ' AND j.id IN %s' % str(
                    tuple(data.get('journal_ids')) + tuple([0]))

            if data.get('account_ids', []):
                WHERE += ' AND a.id IN %s' % str(
                    tuple(data.get('account_ids')) + tuple([0]))

            if data.get('partner_ids', []):
                WHERE += ' AND p.id IN %s' % str(
                    tuple(data.get('partner_ids')) + tuple([0]))

            if data.get('units_ids', []):
                WHERE += ' AND u.id IN %s' % str(
                    tuple(data.get('units_ids')) + tuple([0]))

            if data.get('company_id', False):
                WHERE += ' AND l.company_id = %s' % data.get('company_id')

            if data.get('target_moves') == 'posted_only':
                WHERE += " AND m.state = 'posted'"

            return WHERE

    def build_detailed_move_lines(self, offset=0, partner=0, analytic_account=0 ,fetch_range=FETCH_RANGE):
        '''
        It is used for showing detailed move lines as sub lines. It is defered loading compatable
        :param offset: It is nothing but page numbers. Multiply with fetch_range to get final range
        :param partner: Integer - Partner_id
        :param fetch_range: Global Variable. Can be altered from calling model
        :return: count(int-Total rows without offset), offset(integer), move_lines(list of dict)

        Three sections,
        1. Initial Balance
        2. Current Balance
        3. Final Balance
        '''
        cr = self.env.cr
        data = self.get_filters(default_filters={})
        offset_count = offset * fetch_range
        count = 0
        opening_balance = 0

        currency_id = self.env.company.currency_id

        WHERE = self.build_where_clause()

        WHERE_INIT = WHERE + " AND l.date < '%s'" % data.get('date_from')
        WHERE_INIT += " AND l.partner_id = %s" % partner
        WHERE_INIT += " AND l.analytic_account_id = %s" % analytic_account

        WHERE_CURRENT = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
            'date_to')
        WHERE_CURRENT += " AND p.id = %s" % partner
        # WHERE_CURRENT += " AND pp.analytic_account = %s" account.analytic.account
        if data.get('initial_balance'):
            WHERE_FULL = WHERE + " AND l.date <= '%s'" % data.get('date_to')
        else:
            WHERE_FULL = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                'date_to')
        WHERE_FULL += " AND p.id = %s" % partner
        # WHERE_FULL += " AND pp.analytic_account = %s" account.analytic.account
        ORDER_BY_CURRENT = 'l.date'

        move_lines = []
        if data.get('initial_balance'):
            sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                    --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    --LEFT JOIN product_product pp ON (l.analytic_account_id = pp.analytic_account) -- Join with product_product table
                    WHERE %s
                ''') % WHERE_INIT
            cr.execute(sql)
            row = cr.dictfetchone()
            opening_balance += row.get('balance')

        sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                    --LEFT JOIN product_product pp ON (l.analytic_account_id = pp.analytic_account) -- Join with product_product table
                    --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                    GROUP BY l.date, l.move_id
                    ORDER BY %s
                    OFFSET %s ROWS
                    FETCH FIRST %s ROWS ONLY
                ''') % (WHERE_CURRENT, ORDER_BY_CURRENT, 0, offset_count)
        cr.execute(sql)
        running_balance_list = cr.fetchall()
        for running_balance in running_balance_list:
            opening_balance += running_balance[0]
        sql = ('''
            SELECT COUNT(*)
            FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                --LEFT JOIN product_product pp ON (l.analytic_account_id = pp.analytic_account) -- Join with product_product table
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
            WHERE %s
        ''') % (WHERE_CURRENT)
        cr.execute(sql)
        count = cr.fetchone()[0]
        if (int(offset_count / fetch_range) == 0) and data.get('initial_balance'):
            sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                    --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    --LEFT JOIN product_product pp ON (l.analytic_account_id = pp.analytic_account) -- Join with product_product table
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_INIT
            cr.execute(sql)
            for row in cr.dictfetchall():
                row['move_name'] = 'Initial Balance'
                row['partner_id'] = partner
                row['company_currency_id'] = currency_id.id
                move_lines.append(row)
        sql = ('''
                SELECT
                    l.id AS lid,
                    l.account_id AS account_id,
                    l.partner_id AS partner_id,
                    l.analytic_account_id AS analytic_account_id,
                    l.date AS ldate,
                    j.code AS lcode,
                    l.currency_id,
                    l.amount_currency,
                    l.ref AS lref,
                    l.name AS lname,
                    m.id AS move_id,
                    m.name AS move_name,
                    c.symbol AS currency_symbol,
                    c.position AS currency_position,
                    c.rounding AS currency_precision,
                    cc.id AS company_currency_id,
                    cc.symbol AS company_currency_symbol,
                    cc.rounding AS company_currency_precision,
                    cc.position AS company_currency_position,
                    p.name AS partner_name,
                    --pp.analytic_account product_analytic_account_id,
                    a.name AS account_name,
                    COALESCE(l.debit,0) AS debit,
                    COALESCE(l.credit,0) AS credit,
                    COALESCE(l.debit - l.credit,0) AS balance,
                    COALESCE(l.amount_currency,0) AS amount_currency
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                --LEFT JOIN product_product pp ON (l.analytic_account_id = pp.analytic_account) -- Join with product_product table
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                WHERE %s
                GROUP BY l.id, l.partner_id, a.name, l.account_id, l.date, j.code, l.ref, l.currency_id, l.amount_currency, l.name, m.id, m.name, c.rounding, cc.id, cc.rounding, cc.position, c.position, c.symbol, cc.symbol, p.name
                ORDER BY %s
                OFFSET %s ROWS
                FETCH FIRST %s ROWS ONLY
            ''') % (WHERE_CURRENT, ORDER_BY_CURRENT, offset_count, fetch_range)
        cr.execute(sql)

        for row in cr.dictfetchall():
            current_balance = row['balance']
            row['balance'] = opening_balance + current_balance
            opening_balance += current_balance
            row['initial_bal'] = False
            move_lines.append(row)

        if ((count - offset_count) <= fetch_range) and data.get('initial_balance'):
            sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                    --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    --LEFT JOIN product_product pp ON (l.analytic_account_id = pp.analytic_account) -- Join with product_product table
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_FULL
            cr.execute(sql)
            for row in cr.dictfetchall():
                row['move_name'] = 'Ending Balance'
                row['partner_id'] = partner
                row['company_currency_id'] = currency_id.id
                move_lines.append(row)
        return count, offset_count, move_lines

    def process_data(self):
        '''
        It is the method for showing summary details of each accounts. Just basic details to show up
        Three sections,
        1. Initial Balance
        2. Current Balance
        3. Final Balance
        :return:
        '''
        cr = self.env.cr

        data = self.get_filters(default_filters={})

        WHERE = self.build_where_clause(data)

        partner_company_domain = [('parent_id', '=', False),
                                  '|',
                                  ('customer_rank', '>', 0),
                                  ('supplier_rank', '>', 0),
                                  '|',
                                  ('company_id', '=', self.env.company.id),
                                  ('company_id', '=', False)]
        if self.partner_category_ids:
            partner_company_domain.append(
                ('category_id', 'in', self.partner_category_ids.ids))

        if data.get('partner_ids', []):
            partner_ids = self.env['res.partner'].browse(
                data.get('partner_ids'))
        else:
            partner_ids = self.env['res.partner'].search(
                partner_company_domain)

        move_lines = {
            x.id: {
                'name': x.name,
                'code': x.id,
                'company_currency_id': 0,
                'company_currency_symbol': 'AED',
                'company_currency_precision': 0.0100,
                'company_currency_position': 'after',
                'id': x.id,
                'lines': []
            } for x in partner_ids
        }
        for partner in partner_ids:

            currency = partner.company_id.currency_id or self.env.company.currency_id
            symbol = currency.symbol
            rounding = currency.rounding
            position = currency.position

            opening_balance = 0.0

            WHERE_INIT = WHERE + " AND l.date < '%s'" % data.get('date_from')
            WHERE_INIT += " AND l.partner_id = %s" % partner.id
            ORDER_BY_CURRENT = 'l.date'

            if data.get('initial_balance'):
                sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                    --LEFT JOIN product_product pp ON (l.analytic_account_id = pp.analytic_account) -- Join with product_product table
                    --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_INIT
                cr.execute(sql)
                for row in cr.dictfetchall():
                    row['move_name'] = 'Initial Balance'
                    row['partner_id'] = partner.id
                    row['initial_bal'] = True
                    row['ending_bal'] = False
                    opening_balance += row['balance']
                    move_lines[partner.id]['lines'].append(row)
            WHERE_CURRENT = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                'date_to')
            WHERE_CURRENT += " AND p.id = %s" % partner.id
            sql = ('''
                SELECT
                    l.id AS lid,
                    l.date AS ldate,
                    j.code AS lcode,
                    a.name AS account_name,
                    m.name AS move_name,
                    l.name AS lname,
                    l.ref AS lref,
                    l.analytic_account_id AS analytic_account_id,
                    COALESCE(l.debit,0) AS debit,
                    COALESCE(l.credit,0) AS credit,
                    COALESCE(l.balance,0) AS balance,
                    COALESCE(l.amount_currency,0) AS balance_currency
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                --LEFT JOIN product_product pp ON (l.analytic_account_id = pp.analytic_account) -- Join with product_product table
                --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                WHERE %s
                --GROUP BY l.id, l.account_id, l.date, j.code,l.analytic_account_id, l.currency_id, l.amount_currency, l.ref, l.name, m.id, m.name, c.rounding, cc.rounding, cc.position, c.position, c.symbol, cc.symbol, p.name
                ORDER BY %s
            ''') % (WHERE_CURRENT, ORDER_BY_CURRENT)
            cr.execute(sql)
            current_lines = cr.dictfetchall()
            for row in current_lines:
                row['initial_bal'] = False
                row['ending_bal'] = False

                current_balance = row['balance']
                row['balance'] = opening_balance + current_balance
                opening_balance += current_balance
                row['initial_bal'] = False

                move_lines[partner.id]['lines'].append(row)
            if data.get('initial_balance'):
                WHERE_FULL = WHERE + \
                    " AND l.date <= '%s'" % data.get('date_to')
            else:
                WHERE_FULL = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                    'date_to')
            WHERE_FULL += " AND p.id = %s" % partner.id
            sql = ('''
                SELECT 
                    COALESCE(SUM(l.debit),0) AS debit, 
                    COALESCE(SUM(l.credit),0) AS credit, 
                    COALESCE(SUM(l.debit - l.credit),0) AS balance
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                --LEFT JOIN product_product pp ON (l.analytic_account_id = pp.analytic_account) -- Join with product_product table
                --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                WHERE %s
            ''') % WHERE_FULL
            cr.execute(sql)
            for row in cr.dictfetchall():
                if (data.get('display_accounts') == 'balance_not_zero' and currency.is_zero(
                        row['debit'] - row['credit'])) \
                        or (data.get('balance_less_than_zero') and (row['debit'] - row['credit']) > 0) \
                        or (data.get('balance_greater_than_zero') and (row['debit'] - row['credit']) < 0):
                    move_lines.pop(partner.id, None)
                else:
                    row['ending_bal'] = True
                    row['initial_bal'] = False
                    move_lines[partner.id]['lines'].append(row)
                    move_lines[partner.id]['debit'] = row['debit']
                    move_lines[partner.id]['credit'] = row['credit']
                    move_lines[partner.id]['balance'] = row['balance']
                    move_lines[partner.id]['company_currency_id'] = currency.id
                    move_lines[partner.id]['company_currency_symbol'] = symbol
                    move_lines[partner.id]['company_currency_precision'] = rounding
                    move_lines[partner.id]['company_currency_position'] = position
                    move_lines[partner.id]['count'] = len(current_lines)
                    move_lines[partner.id]['pages'] = self.get_page_list(
                        len(current_lines))
                    move_lines[partner.id]['single_page'] = True if len(
                        current_lines) <= FETCH_RANGE else False
        print('==============move\n\n\n\n\n',move_lines)
        return move_lines

    def get_page_list(self, total_count):
        '''
        Helper function to get list of pages from total_count
        :param total_count: integer
        :return: list(pages) eg. [1,2,3,4,5,6,7 ....]
        '''
        page_count = int(total_count / FETCH_RANGE)
        if total_count % FETCH_RANGE:
            page_count += 1
        return [i + 1 for i in range(0, int(page_count))] or []

    def get_filters(self, default_filters={}):


        company_domain = [('company_id', '=', self.env.company.id)]
        partner_company_domain = [('parent_id', '=', False),
                                  '|',
                                  ('customer_rank', '>', 0),
                                  ('supplier_rank', '>', 0),
                                  '|',
                                  ('company_id', '=', self.env.company.id),
                                  ('company_id', '=', False)]

        journals = self.journal_ids if self.journal_ids else self.env['account.journal'].search(
            company_domain)
        accounts = self.account_ids if self.account_ids else self.env['account.account'].search(
            company_domain)
        partners = self.partner_ids if self.partner_ids else self.env['res.partner'].search(
            partner_company_domain)
        units = self.units_ids if self.units_ids else self.env['product.product'].search(
            company_domain)
        categories = self.partner_category_ids if self.partner_category_ids else self.env[
            'res.partner.category'].search([])

        filter_dict = {
            'journal_ids': self.journal_ids.ids,
            'account_ids': self.account_ids.ids,
            'partner_ids': self.partner_ids.ids,
            'units_ids': self.units_ids.ids,
            'partner_category_ids': self.partner_category_ids.ids,
            'company_id': self.company_id and self.company_id.id or False,
            'target_moves': self.target_moves,
            'initial_balance': self.initial_balance,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'reconciled': self.reconciled,
            'display_accounts': self.display_accounts,
            'include_details': self.include_details,
            'balance_less_than_zero': self.balance_less_than_zero,
            'balance_greater_than_zero': self.balance_greater_than_zero,

            'journals_list': [(j.id, j.name) for j in journals],
            'accounts_list': [(a.id, a.name) for a in accounts],
            'partners_list': [(p.id, p.name) for p in partners],
            'unit_list': [(u.id, u.analytic_account.name) for u in units],
            'category_list': [(c.id, c.name) for c in categories],
            'company_name': self.company_id and self.company_id.name,
        }
        filter_dict.update(default_filters)
        return filter_dict

    def get_report_datas(self, default_filters={}):
        '''
        Main method for pdf, xlsx and js calls
        :param default_filters: Use this while calling from other methods. Just a dict
        :return: All the datas for GL
        '''
        if self.validate_data():
            filters = self.process_filters()
            account_lines = self.process_data()
            return filters, account_lines

    def action_pdf(self):
        filters, account_lines = self.get_report_datas()
        return self.env.ref(
            'partner_ledger_edited'
            '.action_print_partner_ledger_edited').with_context(landscape=True).report_action(
            self, data={'Ledger_data': account_lines,
                        'Filters': filters
                        })

    def print_xls(self):
        self.ensure_one()
        return {
            'name': 'Profit Report',
            'type': 'ir.actions.act_url',
            'url': '/export/partner_report/%s' % (self.id),
        }
        # date_from = fields.Date.from_string(self.date_from).strftime(
        #     self.env['res.lang'].search([('code', '=', self.env.user.lang)])[0].date_format)
        # date_to = fields.Date.from_string(self.date_to).strftime(
        #     self.env['res.lang'].search([('code', '=', self.env.user.lang)])[0].date_format)

        # data = {'from_date': date_from, 'to_date': date_to,
        #         'company_id': self.company_id}
        # print("--------------------------------\n\n\n",self.env.ref('partner_ledger_edited.action_ins_partner_ledger_s_xlsx').report_action(self, data=data))
        # return self.env.ref('partner_ledger_edited.action_ins_partner_ledger_s_xlsx').report_action(self, data=data)

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'PL View',
            'tag': 'dynamic.pl',
            'context': {'wizard_id': self.id}
        }
        return res


class PartnerReportWizardController(http.Controller):
    def convert_to_date(self, datestring=False):
        if datestring:
            lang = request.env.user.lang
            language_id = request.env['res.lang'].search([('code', '=', lang)])[0]
            datestring = fields.Date.from_string(datestring).strftime(language_id.date_format)
            return datetime.datetime.strptime(datestring, language_id.date_format)
        else:
            return False
        
    @http.route(["/export/partner_report/<int:wizard_id>"], type='http', auth='user')
    def export_partner_report(self, wizard_id):
        wizard = request.env['ins.partner.ledger.edited'].browse(wizard_id)
        if not wizard.exists():
            return request.render(
                'http_routing.http_error', {
                    'status_code': 'Oops',
                    'status_message': "Please contact an administrator..."
                }
            )
            
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
            'border': False
        })
        format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            # 'border': True
        })
        content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'border': True,
            'font': 'Arial',
        })
        content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'border': True,
            'align': 'center',
            'font': 'Arial',
        })
        line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'bottom': True,
            'font': 'Arial',
        })
        line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'text_wrap': True,
            'font': 'Arial',
            'valign': 'top'
        })
        line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })
        line_header_light_initial = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'bottom': True,
            'font': 'Arial',
            'valign': 'top'
        })
        line_header_light_ending = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'valign': 'top'
        })

        row_pos = 0
        row_pos_2 = 0

        record = wizard  # Wizard object

        sheet = workbook.add_worksheet('Partner Ledger Edited')
        sheet_2 = workbook.add_worksheet('Filters')
        sheet.set_column(0, 0, 12)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 3, 18)
        sheet.set_column(4, 4, 30)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 10)
        sheet.set_column(7, 7, 10)

        sheet_2.set_column(0, 0, 35)
        sheet_2.set_column(1, 1, 25)
        sheet_2.set_column(2, 2, 25)
        sheet_2.set_column(3, 3, 25)
        sheet_2.set_column(4, 4, 25)
        sheet_2.set_column(5, 5, 25)
        sheet_2.set_column(6, 6, 25)

        sheet.freeze_panes(4, 0)

        sheet.screen_gridlines = False
        sheet_2.screen_gridlines = False
        sheet_2.protect()

        # For Formating purpose
        lang = record.env.user.lang
        lang_id = record.env['res.lang'].search([('code', '=', lang)])[0]
        currency_id = record.env.user.company_id.currency_id
        line_header.num_format = currency_id.excel_format
        line_header_light.num_format = currency_id.excel_format
        line_header_light_initial.num_format = currency_id.excel_format
        line_header_light_ending.num_format = currency_id.excel_format
        line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        content_header_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

        if record:
            data = record.read()
            sheet.merge_range(0, 0, 0, 8, 'Partner Ledger' + ' - ' + data[0]['company_id'][1], format_title)
            filter, acc_lines = record.get_report_datas()
            # Filter section
            # self.prepare_report_filters(filters)

            row_pos_2 = 0
            row_pos_2 += 2
            if filter:
                # print("===================f=============\n\n\n",acc_lines)
                # Date from
                sheet_2.write_string(row_pos_2, 0, _('Date from'),
                                     format_header)
                sheet_2.write_datetime(row_pos_2, 1, self.convert_to_date(str(filter['date_from']) or ''),
                                       content_header_date)
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Date to'),
                                     format_header)
                sheet_2.write_datetime(row_pos_2, 1, self.convert_to_date(str(filter['date_to']) or ''),
                                       content_header_date)
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Target moves'),
                                     format_header)
                sheet_2.write_string(row_pos_2, 1, filter['target_moves'],
                                     content_header)
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Display accounts'),
                                     format_header)
                sheet_2.write_string(row_pos_2, 1, filter['display_accounts'],
                                     content_header)
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Reconciled'),
                                     format_header)
                sheet_2.write_string(row_pos_2, 1, filter['reconciled'],
                                     content_header)
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Initial Balance'),
                                     format_header)
                sheet_2.write_string(row_pos_2, 1, filter['initial_balance'],
                                     content_header)
                row_pos_2 += 1

                # Journals
                row_pos_2 += 2
                sheet_2.write_string(row_pos_2, 0, _('Journals'),
                                     format_header)
                j_list = ', '.join([lt or '' for lt in filter.get('journals')])
                sheet_2.write_string(row_pos_2, 1, j_list,
                                     content_header)

                # Partners
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Partners'),
                                     format_header)
                p_list = ', '.join([lt or '' for lt in filter.get('partners')])
                sheet_2.write_string(row_pos_2, 1, p_list,
                                     content_header)

                # Partner Tags
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Partner Tag'),
                                     format_header)
                p_list = ', '.join([lt or '' for lt in filter.get('categories')])
                sheet_2.write_string(row_pos_2, 1, p_list,
                                     content_header)

                # Accounts
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Accounts'),
                                     format_header)
                a_list = ', '.join([lt or '' for lt in filter.get('accounts')])
                sheet_2.write_string(row_pos_2, 1, a_list,
                                     content_header)

            # Content section
            data = data[0]
            row_pos = 0
            row_pos += 3

            if filter.get('include_details', False):
                sheet.write_string(row_pos, 0, _('Partner'),
                                   format_header)
                sheet.write_string(row_pos, 1, _('Unit'),
                                   format_header)
                sheet.write_string(row_pos, 2, _('JRNL'),
                                   format_header)
                sheet.write_string(row_pos, 3, _('Date'),
                                   format_header)
                sheet.write_string(row_pos, 4, _('Ref'),
                                        format_header)
                sheet.write_string(row_pos, 5, _('Move'),
                                   format_header)
                sheet.write_string(row_pos, 6, _('Entry Label'),
                                   format_header)
                sheet.write_string(row_pos, 7, _('Debit'),
                                   format_header)
                sheet.write_string(row_pos, 8, _('Credit'),
                                   format_header)
                sheet.write_string(row_pos, 9, _('Balance'),
                                   format_header)
            else:
                sheet.merge_range(row_pos, 0, row_pos, 4, _('Partner'), format_header)
                sheet.write_string(row_pos, 5, _('Debit'),
                                   format_header)
                sheet.write_string(row_pos, 6, _('Credit'),
                                   format_header)
                sheet.write_string(row_pos, 7, _('Balance'),
                                   format_header)
            if acc_lines:
                for line in acc_lines:
                    row_pos += 1
                    sheet.merge_range(row_pos, 0, row_pos, 4, acc_lines[line].get('name'), line_header)
                    sheet.write_string(row_pos, 0, acc_lines[line].get('name'),line_header)
                    if acc_lines[line].get('analytic_account_id'):
                        analytic_account = record.env['account.analytic.account'].browse(acc_lines[line].get('analytic_account_id'))
                        sheet.write_string(row_pos, 1, analytic_account.name,line_header_light)
                    sheet.write(row_pos, 2, acc_lines[line].get('lcode'),line_header_light)
                    if acc_lines[line].get('lref'):
                        sheet.write_string(row_pos, 4, acc_lines[line].get('lref'),
                                            line_header_light_date)

                    sheet.write_number(row_pos, 7, float(acc_lines[line].get('debit')), line_header)
                    sheet.write_number(row_pos, 8, float(acc_lines[line].get('credit')), line_header)
                    sheet.write_number(row_pos, 9, float(acc_lines[line].get('balance')), line_header)

                    if filter.get('include_details', False):
                        count, offset, sub_lines = record.build_detailed_move_lines(offset=0, partner=line, fetch_range=1000000)
                        for sub_line in sub_lines:
                            if sub_line.get('move_name') == 'Initial Balance':
                                custom_units = record.env['product.product'].browse(record.units_ids).mapped('analytic_account')
                                row_pos += 1
                                sheet.write_string(row_pos, 0, acc_lines[line].get('name'),line_header)
                                if sub_line.get('analytic_account_id'):
                                    analytic_account = record.env['account.analytic.account'].browse(sub_line.get('analytic_account_id'))
                                    sheet.merge_range(row_pos, 0, row_pos, 1, analytic_account.name, line_header)
                                    sheet.write_string(row_pos, 1, analytic_account.name,line_header)
                                sheet.write(row_pos, 2, sub_line.get('lcode'),line_header_light)
                                if sub_line.get('lref'):
                                    sheet.write_string(row_pos, 4, sub_line.get('lref'),
                                                    line_header_light_date)
                                sheet.write_string(row_pos, 5, sub_line.get('lname') or '',
                                                line_header_light)
                                sheet.write_string(row_pos, 6, sub_line.get('move_name'),
                                                line_header_light_initial)
                                sheet.write_number(row_pos, 7, float(acc_lines[line].get('debit')),
                                                line_header_light_initial)
                                sheet.write_number(row_pos, 8, float(acc_lines[line].get('credit')),
                                                line_header_light_initial)
                                sheet.write_number(row_pos, 9, float(acc_lines[line].get('balance')),
                                                line_header_light_initial)
                            elif sub_line.get('move_name') not in ['Initial Balance', 'Ending Balance']:
                                row_pos += 1
                                sheet.write_string(row_pos, 0, acc_lines[line].get('name'),line_header)
                                if sub_line.get('analytic_account_id'):
                                    analytic_account = record.env['account.analytic.account'].browse(sub_line.get('analytic_account_id'))
                                    sheet.write_string(row_pos, 1, analytic_account.name,line_header)

                                sheet.write_string(row_pos, 2, sub_line.get('lcode'),
                                                line_header_light)
                                sheet.write_datetime(row_pos, 3, self.convert_to_date(sub_line.get('ldate')),
                                                    line_header_light_date)
                                if sub_line.get('lref'):
                                    sheet.write_string(row_pos, 4, sub_line.get('lref'),
                                                    line_header_light_date)
                                sheet.write_string(row_pos, 5, sub_line.get('lname') or '',
                                                line_header_light)
                                sheet.write_string(row_pos, 6, sub_line.get('move_name'),
                                                line_header_light)
                                sheet.write_number(row_pos, 7,
                                                float(sub_line.get('debit')), line_header_light)
                                sheet.write_number(row_pos, 8,
                                                float(sub_line.get('credit')), line_header_light)
                                sheet.write_number(row_pos, 9,
                                                float(sub_line.get('balance')), line_header_light)
                            else:  # Ending Balance
                                row_pos += 1
                                sheet.write_string(row_pos, 0, acc_lines[line].get('name'),line_header)
                                if sub_line.get('analytic_account_id'):
                                    analytic_account = record.env['account.analytic.account'].browse(sub_line.get('analytic_account_id'))
                                    sheet.write_string(row_pos, 1, analytic_account.name,line_header)
                                sheet.write(row_pos, 2, sub_line.get('lcode'),line_header_light)
                                if sub_line.get('lref'):
                                    sheet.write_string(row_pos, 4, sub_line.get('lref'),
                                                    line_header_light_date)
                                sheet.write_string(row_pos, 5, sub_line.get('lname') or '',
                                                line_header_light)
                                sheet.write_string(row_pos, 6, sub_line.get('move_name'),
                                                line_header_light_ending)
                                sheet.write_number(row_pos, 7, float(acc_lines[line].get('debit')),
                                                line_header_light_ending)
                                sheet.write_number(row_pos, 8, float(acc_lines[line].get('credit')),
                                                line_header_light_ending)
                                sheet.write_number(row_pos, 9, float(acc_lines[line].get('balance')),
                                                line_header_light_ending)
        # if acc_lines:
            #     row_pos += 1
            #     # sheet.write_string(row_pos, 1, acc_lines[line].get('name'),line_header)
            #     # sheet.write(row_pos, 2, sub_line.get('lcode'),line_header_light)

            #     # sheet.write_number(row_pos, 7, float(sub_line.get('debit')), line_header)
            #     # sheet.write_number(row_pos, 8, float(sub_line.get('credit')), line_header)
            #     # sheet.write_number(row_pos, 9, float(sub_line.get('balance')), line_header)
            #     for partner, analytic_accounts in acc_lines.items():

            #         if filter.get('include_details', False):
            #             print("===================5=============\n\n\n")
            #             # if len(record.units_ids) > 0:
            #             # count, offset, sub_lines = record.build_detailed_move_lines(offset=0, partner=partner, fetch_range=1000000)
            #             if not analytic_accounts['lines']:
            #     #         # If there are no records, skip to the next iteration
            #                 continue
            #             for l in analytic_accounts['lines']:
            #                 sub_lines = l['lines']
            #                 for sub_line in analytic_accounts['lines']:
            #                     sheet.merge_range(row_pos, 0, row_pos, 4, analytic_accounts.get('name'), line_header)
            #                     if sub_line.get('move_name') == 'Initial Balance':
            #                         custom_units = record.env['product.product'].browse(record.units_ids).mapped('analytic_account')
            #                         print("===================units=============\n\n\n",sub_line)
            #                         row_pos += 1
            #                         # sheet.write_string(row_pos, 0, analytic_accounts.get('name'),line_header)
            #                         sheet.write(row_pos, 2, sub_line.get('lcode'),line_header_light)
            #                         sheet.write_string(row_pos, 6, sub_line.get('move_name'),
            #                                             line_header_light_initial)
            #                         sheet.write_number(row_pos, 7, float(sub_line.get('debit')),
            #                                             line_header_light_initial)
            #                         sheet.write_number(row_pos, 8, float(sub_line.get('credit')),
            #                                             line_header_light_initial)
            #                         sheet.write_number(row_pos, 9, float(sub_line.get('balance')),
            #                                             line_header_light_initial)
            #                     elif sub_line.get('move_name') not in ['Initial Balance', 'Ending Balance']:
            #                         print("===================6=============\n\n\n")
            #                         row_pos += 1
            #                         sheet.write_datetime(row_pos, 0, self.convert_to_date(sub_line.get('ldate')),
            #                                                 line_header_light_date)
            #                         sheet.write_string(row_pos, 1, sub_line.get('lcode'),
            #                                             line_header_light)
            #                         sheet.write_string(row_pos, 2, sub_line.get('account_name') or '',
            #                                             line_header_light)
            #                         sheet.write_string(row_pos, 3, sub_line.get('lref') or '',
            #                                                 line_header_light)
            #                         sheet.write_string(row_pos, 3, sub_line.get('move_name'),
            #                                             line_header_light)
            #                         sheet.write_string(row_pos, 4, sub_line.get('lname') or '',
            #                                             line_header_light)
            #                         sheet.write_number(row_pos, 5,
            #                                             float(sub_line.get('debit')), line_header_light)
            #                         sheet.write_number(row_pos, 6,
            #                                             float(sub_line.get('credit')), line_header_light)
            #                         sheet.write_number(row_pos, 7,
            #                                             float(sub_line.get('balance')), line_header_light)
            #                     else:  # Ending Balance
            #                         print("===================7=============\n\n\n",sub_line.get('lcode'))
            #                         row_pos += 1
            #                         # sheet.write_string(row_pos, 0, acc_lines[line].get('name'),line_header)
            #                         sheet.write(row_pos, 2, sub_line.get('lcode'),line_header_light)


            #                         sheet.write_string(row_pos, 6, sub_line.get('move_name'),
            #                                             line_header_light_ending)
            #                         sheet.write_number(row_pos, 7, float(sub_line.get('debit')),
            #                                             line_header_light_ending)
            #                         sheet.write_number(row_pos, 8, float(sub_line.get('credit')),
            #                                             line_header_light_ending)
            #                         sheet.write_number(row_pos, 9, float(sub_line.get('balance')),
            #                                             line_header_light_ending)
                # for partner, analytic_accounts in acc_lines.items():
                #     if not analytic_accounts['lines']:
                #         # If there are no records, skip to the next iteration
                #         continue
                #     row_pos += 1
                #     partner_name = wizard.env['res.partner'].browse(partner).name
                #     print('=================partner===============================================\n\n', partner_name)
                #     sheet.merge_range(row_pos, 0, row_pos, 4, partner_name, line_header)
                #     # sheet.write(row_pos, 0, partner, line_header)


                #     for account_data in analytic_accounts['lines']:
                #         account_name = account_data['name']
                #         records = account_data['lines']

                #         row_pos += 1
                #         sheet.merge_range(row_pos, 0, row_pos, 4, account_name, line_header_light)
                #         sheet.merge_range(row_pos, 0, row_pos, 4, account_name, line_header_light)

                #         for record in records:
                #             # print('===================record=============================================\n\n', record)
                #             # print('===================record==jj===========================================\n\n', record.get('lines'))
                #             # print('===================record=ki============================================\n\n', record.lines)
                #             if record.get('lines'):
                #                 for i in record.get('lines'):
                #                     row_pos += 1
                #                     sheet.write_datetime(row_pos, 0, self.convert_to_date(i['ldate']), line_header_light_date)
                #                     sheet.write(row_pos, 1, i['lcode'], line_header_light)
                #                     sheet.write(row_pos, 2, i['account_name'] or '', line_header_light)
                #                     sheet.write(row_pos, 3, i['lref'] or '', line_header_light)
                #                     sheet.write(row_pos, 4, i['move_name'], line_header_light)
                #                     sheet.write(row_pos, 5, i['lname'] or '', line_header_light)
                #                     sheet.write(row_pos, 6, float(i['debit']), line_header_light)
                #                     sheet.write(row_pos, 7, float(i['credit']), line_header_light)
                #                     sheet.write(row_pos, 8, float(i['balance']), line_header_light)






            #     # print("===================acc=============\n\n\n============\n\n",acc_lines)
            # #      = {
            # #     # ... (your dictionary here)
            # # }data_dict

            # # Loop through the dictionary and extract the 'name' field from each line
            #     for partner_id, partner_data in acc_lines.items():
            #     #     if 'lines' in partner_data:
            #     #         print(f"\n\nLine Name\n\n: {partner_data.get('name')}")
            #     #         print(f"Partner ID: {partner_id}, Name: {partner_data['name']}")
            #     #         for line in partner_data['lines']:
            #     #             line_name = line.get('name', 'Undefined')
            #     #             print(f"\n\nLine Name\n\n: {line_name}")

            #     # for line in acc_lines:
            #         # for line_line in sub_line:
            #             # data_list = sub_line[line_line]
            #             # print("===================4=============\n\n\n============\n\n",data_list)
            #             # if isinstance(data, list) and 'name' in data:
            #             #     for line in data['lines']:
            #             #         if isinstance(line, dict) and 'name' in line:
            #             #             # print(l.ine['name'])
            #                 # print(data['name'])
            #             # print(f"===================4=lines============\n\n\n============{sub_line[line_line]['name']}\n\n")
            #         row_pos += 1
            #         sheet.merge_range(row_pos, 0, row_pos, 4, partner_data.get('name'), line_header)
            #         row_pos += 1
            #         # sheet.merge_range(row_pos, 1, row_pos, 3, sub_line['lines'], line_header)
            #         sheet.write_string(row_pos, 0, partner_data.get('name'),line_header)
            #         # if sub_line.get('analytic_account_id'):
            #         #     analytic_account = record.env['account.analytic.account'].browse(sub_line.get('analytic_account_id'))
            #         #     sheet.write_string(row_pos, 1, analytic_account.name,line_header)
            #         # sheet.write(row_pos, 2, sub_line.get('lcode'),line_header_light)
            #         # if sub_line.get('lref'):
            #         #     sheet.write_string(row_pos, 4, sub_line.get('lref'),
            #         #                         line_header_light_date)

            #         # sheet.write_number(row_pos, 7, float(sub_line.get('debit')), line_header)
            #         # sheet.write_number(row_pos, 8, float(sub_line.get('credit')), line_header)
            #         # sheet.write_number(row_pos, 9, float(sub_line.get('balance')), line_header)

            #         for line in partner_data['lines']:
            #             print("===================line=============\n\n\n",line)
            #             row_pos += 1
            #             if filter.get('include_details', False):
            #                 if line.get('name', 'Undefined'):
            #                     line_name = line.get('name', 'Undefined')
            #                     print("===================line_name1=============\n\n\n",line_name)
            #                     sheet.merge_range(row_pos, 0, row_pos, 1, line_name, line_header)
            #                 count, offset, sub_lines = record.build_detailed_move_lines(offset=0, partner=partner_id, fetch_range=1000000)
            #                 for sub_line in sub_lines:
            #                     if sub_line.get('move_name') == 'Initial Balance':
            #                         custom_units = record.env['product.product'].browse(record.units_ids).mapped('analytic_account')
            #                         # print("===================ref5=============\n\n\n",sub_line.get('lref'))
            #                         row_pos += 1
            #                         if line.get('name', 'Undefined'):
            #                             line_name = line.get('name', 'Undefined')
            #                             print("===================line_name1=============\n\n\n",line_name)
            #                         # line_name = line.get('name', 'Undefined')
            #                         # print("===================line_name2=============\n\n\n",line_name)
            #                         # sheet.write_string(row_pos, 0, line.get('name'),line_header)
            #                         # if sub_line.get('analytic_account_id'):
            #                         #     analytic_account = record.env['account.analytic.account'].browse(sub_line.get('analytic_account_id'))
            #                         #     sheet.write_string(row_pos, 1, analytic_account.name,line_header)
            #                         sheet.write(row_pos, 2, line.get('lcode'),line_header_light)
            #                         if line.get('lref'):
            #                             sheet.write_string(row_pos, 4, line.get('lref'),
            #                                             line_header_light_date)
            #                         # sheet.write_string(row_pos, 5, sub_line.get('lname') or '',
            #                         #                 line_header_light)
            #                         # sheet.write_string(row_pos, 6, sub_line.get('move_name'),
            #                         #                 line_header_light_initial)
            #                         # sheet.write_number(row_pos, 7, float(sub_line.get('debit')),
            #                         #                 line_header_light_initial)
            #                         # sheet.write_number(row_pos, 8, float(sub_line.get('credit')),
            #                         #                 line_header_light_initial)
            #                         # sheet.write_number(row_pos, 9, float(sub_line.get('balance')),
            #                         #                 line_header_light_initial)
            #                     elif sub_line.get('move_name') not in ['Initial Balance', 'Ending Balance']:
            #                         row_pos += 1
            #                         if line.get('name', 'Undefined'):
            #                             line_name = line.get('name', 'Undefined')
            #                             print("===================line_name21=============\n\n\n",line_name)
            #                         # line_name = line.get('name', 'Undefined')
            #                         # print("===================line_name3=============\n\n\n",line_name)
            #                         # sheet.write_string(row_pos, 0, line.get('name'),line_header)
            #                         # if sub_line.get('analytic_account_id'):
            #                         #     analytic_account = record.env['account.analytic.account'].browse(sub_line.get('analytic_account_id'))
            #                         #     sheet.write_string(row_pos, 1, analytic_account.name,line_header)

            #                         sheet.write_string(row_pos, 2, line.get('lcode'),
            #                                         line_header_light)
            #                         # sheet.write_datetime(row_pos, 3, self.convert_to_date(sub_line.get('ldate')),
            #                         #                     line_header_light_date)
            #                         # if sub_line.get('lref'):
            #                         #     sheet.write_string(row_pos, 4, sub_line.get('lref'),
            #                         #                     line_header_light_date)
            #                         # sheet.write_string(row_pos, 5, sub_line.get('lname') or '',
            #                         #                 line_header_light)
            #                         # sheet.write_string(row_pos, 6, sub_line.get('move_name'),
            #                         #                 line_header_light)
            #                         # sheet.write_number(row_pos, 7,
            #                         #                 float(sub_line.get('debit')), line_header_light)
            #                         # sheet.write_number(row_pos, 8,
            #                         #                 float(sub_line.get('credit')), line_header_light)
            #                         # sheet.write_number(row_pos, 9,
            #                         #                 float(sub_line.get('balance')), line_header_light)
            #                     else:  # Ending Balance
            #                         row_pos += 1
            #                         if line.get('name', 'Undefined'):
            #                             line_name = line.get('name', 'Undefined')
            #                             print("===================line_name31=============\n\n\n",line_name)
            #                         # line_name = line.get('name', 'Undefined')
            #                         # print("===================line_name4=============\n\n\n",line_name)
            #                         # sheet.write_string(row_pos, 0, line.get('name'),line_header)
            #                         # if sub_line.get('analytic_account_id'):
            #                         #     analytic_account = record.env['account.analytic.account'].browse(sub_line.get('analytic_account_id'))
            #                         #     sheet.write_string(row_pos, 1, analytic_account.name,line_header)
            #                         sheet.write(row_pos, 2, line.get('lcode'),line_header_light)
            #                         if line.get('lref'):
            #                             sheet.write_string(row_pos, 4, line.get('lref'),
            #                                             line_header_light_date)
            #                         # sheet.write_string(row_pos, 5, sub_line.get('lname') or '',
            #                         #                 line_header_light)
            #                         # sheet.write_string(row_pos, 6, sub_line.get('move_name'),
            #                         #                 line_header_light_ending)
            #                         # sheet.write_number(row_pos, 7, float(sub_line.get('debit')),
            #                         #                 line_header_light_ending)
            #                         # sheet.write_number(row_pos, 8, float(sub_line.get('credit')),
            #                         #                 line_header_light_ending)
            #                         # sheet.write_number(row_pos, 9, float(sub_line.get('balance')),
            #                         #                 line_header_light_ending)
        workbook.close()

        xlsx_data = output.getvalue()
        response = request.make_response(
            xlsx_data,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=Profit Report-' + datetime.date.today().strftime('%Y.%m.%d')+ '.xlsx')],
        )
        return response
        