# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class RentSaleOrder(models.Model):
    _inherit = 'sale.order'

    plus_year = fields.Boolean(string="اكثر من سنة")
    years_number = fields.Integer(string="عدد السنين")

    @api.onchange('years_number', 'fromdate')
    def _compute_to_date(self):
        for rec in self:
            if rec.years_number and rec.fromdate:
                rec.todate = rec.fromdate + relativedelta(years=rec.years_number)


class RentSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    year_number = fields.Integer(string="رقم السنة")
    fromdate = fields.Datetime(string='From Date', copy=True)
    todate = fields.Datetime(string='To Date', copy=True)

    @api.onchange('year_number')
    def _compute_dates(self):
        for rec in self:
            if rec.year_number and rec.order_id.fromdate:
                if rec.year_number == 1:
                    fromdate = rec.fromdate = rec.order_id.fromdate
                    rec.todate = fromdate + relativedelta(years=1)

                if rec.year_number == 2:
                    fromdate = rec.fromdate = self.env['sale.order.line'].search([('year_number', '=', 1)],limit=1).mapped('todate')[0]
                    rec.todate = fromdate + relativedelta(years=1)

                if rec.year_number == 3:
                    fromdate = rec.fromdate = self.env['sale.order.line'].search([('year_number', '=', 2)],limit=1).mapped('todate')[0]
                    rec.todate = fromdate + relativedelta(years=1)

                if rec.year_number == 4:
                    fromdate = rec.fromdate = self.env['sale.order.line'].search([('year_number', '=', 3)],limit=1).mapped('todate')[0]
                    rec.todate = fromdate + relativedelta(years=1)

                if rec.year_number == 5:
                    fromdate = rec.fromdate = self.env['sale.order.line'].search([('year_number', '=', 4)],limit=1).mapped('todate')[0]
                    rec.todate = fromdate + relativedelta(years=1)


    # @api.constrains('year_number')
    # def _check_year_number(self):
    #     for rec in self:
    #         if rec.year_number:
    #             order = self.env['sale.order.line'].search([('order_id', '=', rec.order_id.id)]).mapped('year_number')
    #             print("////////////////////////////",order)
    #             if rec.price_unit < rec.rental_pricing_id.price :
    #                 raise ValidationError("Price of %s can not be less than rental pricing price !" %rec.product_id.name)
