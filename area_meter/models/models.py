# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class RentProduct(models.Model):
    _inherit = 'product.template'

    rent_unit_area = fields.Float(string='المساحة m2', copy=True)
    rent_unit_area_price = fields.Float(string='سعر المتر', copy=True)


class RentRentalPricing(models.Model):
    _inherit = 'rental.pricing'

    rent_unit_area = fields.Float(string='المساحة m2', copy=True, readonly=False)
    rent_unit_area_price = fields.Float(string='سعر المتر', copy=True, readonly=False)
    price = fields.Monetary(string="Price", required=True, default=1.0, readonly=False, compute="_compute_price_rent")

    @api.onchange('rent_unit_area', 'rent_unit_area_price', 'duration')
    def _compute_price_rent(self):
        for rec in self:
            rec.price = rec.rent_unit_area * rec.rent_unit_area_price * rec.duration


class RentSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rent_unit_area = fields.Float(string='المساحة m2', copy=True, readonly=False)
    rent_unit_area_price = fields.Float(string='سعر المتر', copy=True, readonly=False)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)

    @api.onchange('product_id')
    def get_area_price_rent(self):
        for rec in self:
            rec.rent_unit_area = rec.product_id.rent_unit_area
            rec.rent_unit_area_price = rec.product_id.rent_unit_area_price

    @api.onchange('rent_unit_area', 'rent_unit_area_price', 'product_id')
    def _compute_price_rent(self):
        for rec in self:
            rec.price_unit = rec.rent_unit_area * rec.rent_unit_area_price * rec.rental_pricing_id.duration

    @api.constrains('price_unit')
    def _compute_price_unit_rental_pricing(self):
        for rec in self:
            if self.user_has_groups('area_meter.rental_pricing_user') and not self.user_has_groups(
                    'area_meter.rental_pricing_manager'):
                if rec.price_unit < rec.rental_pricing_id.price:
                    raise ValidationError(
                        "Price of %s can not be less than rental pricing price !" % rec.product_id.name)
