# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RestorationDeadline(models.Model):
    _name = 'restoration.deadline'

    name = fields.Char("المهلة")


class OfferValidity(models.Model):
    _name = 'offer.validity'

    name = fields.Char("الصلاحية")


class RentSaleOrder(models.Model):
    _inherit = 'sale.order'

    restoration_deadline = fields.Many2one("restoration.deadline", string='مهلة الترميم')
    offer_validity = fields.Many2one("offer.validity", string='صلاحية العرض')
