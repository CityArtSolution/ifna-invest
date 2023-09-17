# -*- coding: utf-8 -*-

from odoo import models, fields, api
from hijri_converter import Hijri, Gregorian


class RentRentalWizardInherit(models.TransientModel):
    _inherit = 'rental.wizard'


    duration_unit = fields.Selection(
        [("hour", "Hours"), ("day", "Days"), ("week", "Weeks"), ("month", "Months"), ("year", "years")],
        string="Unit", required=True, compute="_compute_duration")

    hijri_pickup_date = fields.Date()
    hijri_return_date = fields.Date()
    geo_pickup_date = fields.Date()
    geo_return_date = fields.Date()
    # hijri_pickup_date = fields.Char(compute='_compute_hijri_dates')
    # hijri_return_date = fields.Char(compute='_compute_hijri_dates')


    @api.onchange('geo_pickup_date','geo_return_date')
    def _compute_geogrian_dates(self):
        for rec in self:
            if rec.geo_pickup_date:
                rec.pickup_date = rec.pickup_date.replace(day = rec.geo_pickup_date.day, month= rec.geo_pickup_date.month, year= rec.geo_pickup_date.year)

            if rec.geo_return_date:
                rec.return_date = rec.return_date.replace(day = rec.geo_return_date.day, month= rec.geo_return_date.month, year= rec.geo_return_date.year)



    # @api.onchange('pickup_date','return_date')
    # def _compute_hijri_dates(self):
    #     for rec in self:
    #         if rec.pickup_date:
    #             rec.hijri_pickup_date = Gregorian(rec.pickup_date.date().year, rec.pickup_date.date().month,
    #                                               rec.pickup_date.date().day).to_hijri()
    #         else:
    #             rec.hijri_pickup_date = ''
    #
    #         if rec.return_date:
    #             rec.hijri_return_date = Gregorian(rec.return_date.date().year, rec.return_date.date().month,
    #                                               rec.return_date.date().day).to_hijri()
    #         else:
    #             rec.hijri_return_date = ''
