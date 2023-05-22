# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class RentProduct(models.Model):
    _inherit = 'product.template'

    rent_unit_area = fields.Float(string='المساحة m2', copy=True)
    rent_unit_area_price = fields.Float(string='سعر المتر', copy=True)


class RentRentalPricing(models.Model):
    _inherit = 'rental.pricing'

    rent_unit_area = fields.Float(string='المساحة m2', copy=True, related="product_template_id.rent_unit_area", readonly=False)
    rent_unit_area_price = fields.Float(string='سعر المتر', copy=True,
                                        related="product_template_id.rent_unit_area_price", readonly=False)
    price = fields.Monetary(string="Price", required=True, default=1.0, readonly=False)

    @api.onchange('rent_unit_area','rent_unit_area_price')
    def _compute_price(self):
        """Compute the price for a specified duration of the current pricing rule.

        :param float duration: duration in hours
        :param str unit: duration unit (hour, day, week)
        :return float: price
        """
        for rec in self:
            rec.price = rec.rent_unit_area * rec.rent_unit_area_price


class RentSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rent_unit_area = fields.Float(string='المساحة m2', copy=True, related="rental_pricing_id.rent_unit_area", readonly=False)
    rent_unit_area_price = fields.Float(string='سعر المتر', copy=True, related="rental_pricing_id.rent_unit_area_price", readonly=False)

    @api.constrains('price_unit')
    def _check_price_unit_rental_pricing(self):
        for rec in self:
            if rec.price_unit:
                if rec.price_unit < rec.rental_pricing_id.price :
                    raise ValidationError("Price of %s can not be less than rental pricing price !" %rec.product_id.name)
