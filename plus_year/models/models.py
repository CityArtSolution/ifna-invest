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

    year_number = fields.Integer()
    fromdate = fields.Datetime(string='From Date', copy=True)
    todate = fields.Datetime(string='To Date', copy=True)
    test = fields.Integer(related='order_id.years_number', readonly=True, store=True)
    line_sequence = fields.Integer(string='Line Sequence', copy=False, default=100)

    @api.model
    def create(self, values):
        order = values['order_id']
        if 'line_sequence' in values and 'property_number' in values:
            values['line_sequence'] = self._get_next_line_sequence(order)
        return super().create(values)

    @api.model
    def _get_next_line_sequence(self, order):
        last_line = self.env['sale.order.line'].search([('order_id', '=', order), ('property_number', '!=', False)],
                                                       order='line_sequence desc', limit=1)
        if last_line:
            return last_line.line_sequence + 100
        return 100

    # @api.onchange('year_number')
    # def check_year_number(self):
    #     if not (self.year_number >= 0 and self.year_number <= self.order_id.years_number):
    #         raise UserError(f"رقم السنه يجب ان يكون اقل من او يساوي {self.order_id.years_number}")

    @api.onchange('year_number')
    def _compute_dates(self):
        for rec in self:
            if not (rec.year_number >= 0 and rec.year_number <= rec.order_id.years_number):
                raise UserError(f"رقم السنه يجب ان يكون اقل من او يساوي {rec.order_id.years_number}")

            if rec.year_number and rec.order_id.fromdate:
                if rec.year_number == 1:
                    fromdate = rec.fromdate = rec.order_id.fromdate
                    rec.todate = fromdate + relativedelta(years=1)

                if rec.year_number == 2:
                    date = self.env['sale.order.line'].search([('year_number', '=', 1)], limit=1).mapped('todate')
                    if date:
                        fromdate = rec.fromdate = date[0]
                        rec.todate = fromdate + relativedelta(years=1)

                if rec.year_number == 3:
                    date = self.env['sale.order.line'].search([('year_number', '=', 2)], limit=1).mapped('todate')
                    if date:
                        fromdate = rec.fromdate = date[0]
                        rec.todate = fromdate + relativedelta(years=1)

                if rec.year_number == 4:
                    date = self.env['sale.order.line'].search([('year_number', '=', 3)], limit=1).mapped('todate')
                    if date:
                        fromdate = rec.fromdate = date[0]
                        rec.todate = fromdate + relativedelta(years=1)

                if rec.year_number == 5:
                    date = self.env['sale.order.line'].search([('year_number', '=', 4)], limit=1).mapped('todate')
                    if date:
                        fromdate = rec.fromdate = date[0]
                        rec.todate = fromdate + relativedelta(years=1)

    # @api.constrains('year_number')
    # def _check_year_number(self):
    #     for rec in self:
    #         if rec.year_number:
    #             order = self.env['sale.order.line'].search([('order_id', '=', rec.order_id.id)]).mapped('year_number')
    #             print("////////////////////////////",order)
    #             if rec.price_unit < rec.rental_pricing_id.price :
    #                 raise ValidationError("Price of %s can not be less than rental pricing price !" %rec.product_id.name)
