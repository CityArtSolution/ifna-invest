# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class RentSaleOrder(models.Model):
    _inherit = 'sale.order'

    plus_year = fields.Boolean(string="اكثر من سنة", store=True)
    years_number = fields.Integer(string="عدد السنين", store=True)
    years = fields.Char(string='Years', store=True)

    @api.onchange('years_number', 'fromdate')
    def _compute_to_date(self):
        for rec in self:
            if rec.years_number and rec.fromdate:
                rec.todate = rec.fromdate + relativedelta(years=rec.years_number)


class RentSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _order = 'line_sequence'

    year_number = fields.Integer(related="order_id.years_number", store=True, readonly=False)
    line_year_number = fields.Integer(string="رقم السنه", copy=False, default=1)
    fromdate = fields.Datetime(string='From Date', copy=True)
    todate = fields.Datetime(string='To Date', copy=True)
    line_sequence = fields.Integer(string='Line Sequence', copy=False, default=100)

    @api.model
    def create(self, values):
        order = values['order_id']
        if 'line_sequence' in values and 'property_number' in values:
            values['line_sequence'] = self._get_next_line_sequence(order)
            values['line_year_number'] = self._get_next_line_year_number(order)
        return super().create(values)

    @api.model
    def _get_next_line_sequence(self, order):
        last_line = self.env['sale.order.line'].search([('order_id', '=', order), ('property_number', '!=', False)],
                                                       order='line_sequence desc', limit=1)
        if last_line:
            return last_line.line_sequence + 100
        return 100

    @api.onchange('line_year_number')
    def _compute_dates(self):
        for rec in self:
            if not (rec.line_year_number >= 0 and rec.line_year_number <= rec.order_id.years_number):
                raise UserError(f"رقم السنه يجب ان يكون اقل من او يساوي {rec.order_id.years_number}")

            if rec.line_year_number and rec.order_id.fromdate:
                if rec.line_year_number == 1:
                    fromdate = rec.fromdate = rec.order_id.fromdate
                    rec.todate = fromdate + relativedelta(years=1)

                if rec.line_year_number == 2:
                    date = self.env['sale.order.line'].search([('line_year_number', '=', 1)], limit=1).mapped('todate')
                    if date:
                        fromdate = rec.fromdate = date[0]
                        rec.todate = fromdate + relativedelta(years=1)

                if rec.line_year_number == 3:
                    date = self.env['sale.order.line'].search([('line_year_number', '=', 2)], limit=1).mapped('todate')
                    if date:
                        fromdate = rec.fromdate = date[0]
                        rec.todate = fromdate + relativedelta(years=1)

                if rec.line_year_number == 4:
                    date = self.env['sale.order.line'].search([('line_year_number', '=', 3)], limit=1).mapped('todate')
                    if date:
                        fromdate = rec.fromdate = date[0]
                        rec.todate = fromdate + relativedelta(years=1)

                if rec.line_year_number == 5:
                    date = self.env['sale.order.line'].search([('line_year_number', '=', 4)], limit=1).mapped('todate')
                    if date:
                        fromdate = rec.fromdate = date[0]
                        rec.todate = fromdate + relativedelta(years=1)

    @api.model
    def _get_next_line_year_number(self, order):
        last_line = self.env['sale.order.line'].search([('order_id', '=', order), ('property_number', '!=', False)],
                                                       order='line_sequence desc', limit=1)
        if last_line:
            return last_line.line_year_number + 1
        return 1

    @api.onchange('line_year_number')
    def check_year_number(self):
        if not (self.line_year_number >= 0 and self.line_year_number <= self.order_id.years_number):
            raise UserError(f"رقم السنه يجب ان يكون اقل من او يساوي {self.order_id.years_number}")
