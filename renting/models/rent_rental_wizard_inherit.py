# -*- coding: utf-8 -*-

from odoo import models, fields, api
from hijri_converter import Hijri, Gregorian


class RentRentalWizardInherit(models.TransientModel):
    _inherit = 'rental.wizard'

    duration_unit = fields.Selection(
        [("hour", "Hours"), ("day", "Days"), ("week", "Weeks"), ("month", "Months"), ("year", "years")],
        string="Unit", required=True, compute="_compute_duration")

    hijri_pickup_date = fields.Char(compute='_compute_hijri_dates')
    hijri_return_date = fields.Char(compute='_compute_hijri_dates')


    @api.onchange('pickup_date','return_date')
    def _compute_hijri_dates(self):
        for rec in self:
            if rec.pickup_date:
                rec.hijri_pickup_date = Gregorian(rec.pickup_date.date().year, rec.pickup_date.date().month,
                                                  rec.pickup_date.date().day).to_hijri()
            else:
                rec.hijri_pickup_date = ''

            if rec.return_date:
                rec.hijri_return_date = Gregorian(rec.pickup_date.date().year, rec.pickup_date.date().month,
                                                  rec.pickup_date.date().day).to_hijri()
            else:
                rec.hijri_return_date = ''
