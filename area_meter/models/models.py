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
    price = fields.Monetary(string="Price", required=True, default=1.0, readonly=False)


class RentalWizard(models.TransientModel):
    _inherit = 'rental.wizard'

    rent_unit_area = fields.Float(string='المساحة m2', copy=True,
                                  readonly=False, related="product_id.product_tmpl_id.rent_unit_area")
    rent_unit_area_price = fields.Float(string='سعر المتر', copy=True,
                                        readonly=False, related="product_id.product_tmpl_id.rent_unit_area_price")

    @api.model
    # def write(self, vals):
    #     res = super(RentalWizard, self).write(vals)
    #     active_ids = self.env.context.get("active_ids")
    #     active_id = self.env.context.get('active_id')
    #     print('wwwwwwwwwwwwwwwwwwwwwwww', self.read())
    #     print('wwwwwwwwwwwwwwwwwwwwwwww', self._origin)
    #     print('wwwwwwwwwwwwwwwwwwwwwwww', self._origin.id)
    #     print('wwwwwwwwwwwwwwwwwwwwwwww', self._origin.rental_order_line_id)
    #     print('wwwwwwwwwwwwwwwwwwwwwwww', self.rental_order_line_id)
    #     print('wwwwwwwwwwwwwwwwwwwwwwww', self.rental_order_line_id)
    #     print('wwwwwwwwwwwwwwwwwwwwwwww', active_ids)
    #     print('wwwwwwwwwwwwwwwwwwwwwwww', active_id)
    #     return res
    # @api.model
    # def create(self, vals):
    #     print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
    #     print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",self._origin)
    #     print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",self._origin.id)
    #     print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",self.rental_order_line_id._origin.id)
    #     print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwww", vals.get('rental_order_line_id'))
    #     return super(RentalWizard, self).create(vals)

    def save_data(self):
        active_ids = self.env.context.get("active_ids")
        active_id = self.env.context.get('active_id')
        print('/////////////////////////////////////', self.read())
        print('/////////////////////////////////////', self._origin)
        print('/////////////////////////////////////', self._origin.id)
        print('/////////////////////////////////////', self._origin.rental_order_line_id)
        print('/////////////////////////////////////', self.rental_order_line_id)
        print('///////////////////////rental_order_line_id//////////////', self.rental_order_line_id)
        print('/////////////////////////////////////', active_ids)
        print('/////////////////////////////////////', active_id)
        # print('///////////////////////rent_unit_area//////////////',self.rent_unit_area)
        # print('///////////////////////rent_unit_area_price//////////////',self.rent_unit_area_price)
        self.rental_order_line_id.rent_unit_area = self.rent_unit_area
        self.rental_order_line_id.rent_unit_area_price = self.rent_unit_area_price
        self.rental_order_line_id.write({'rent_unit_area': self.rent_unit_area,
                                         'rent_unit_area_price': self.rent_unit_area_price})

    @api.onchange('rent_unit_area', 'rent_unit_area_price')
    def _compute_price_rent(self):
        for rec in self:
            rec.rental_order_line_id.write({'rent_unit_area': rec.rent_unit_area,
                                            'rent_unit_area_price': rec.rent_unit_area_price})
            rec.unit_price = rec.rent_unit_area * rec.rent_unit_area_price * rec.duration

    # @api.onchange('pricing_id', 'currency_id', 'duration', 'duration_unit')
    # def _compute_area_meter(self):
    #     for wizard in self:
    #         if wizard.pricing_id and wizard.duration > 0:
    #             unit_price = wizard.pricing_id._compute_price(wizard.duration, wizard.duration_unit)
    #             if wizard.currency_id != wizard.pricing_id.currency_id:
    #                 wizard.unit_price = wizard.pricing_id.currency_id._convert(
    #                     from_amount=unit_price,
    #                     to_currency=wizard.currency_id,
    #                     company=wizard.company_id)
    #             else:
    #                 wizard.unit_price = unit_price
    #         elif wizard.duration > 0:
    #             wizard.unit_price = wizard.product_id.lst_price


class RentSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rent_unit_area = fields.Float(string='المساحة m2', copy=True)
    rent_unit_area_price = fields.Float(string='سعر المتر', copy=True)

    @api.constrains('price_unit')
    def _check_price_unit_rental_pricing(self):
        for rec in self:
            if rec.price_unit:
                if self.user_has_groups('area_meter.rental_pricing_user') and not self.user_has_groups(
                        'area_meter.rental_pricing_manager'):
                    if rec.price_unit < rec.rental_pricing_id.price:
                        raise ValidationError(
                            "Price of %s can not be less than rental pricing price !" % rec.product_id.name)
