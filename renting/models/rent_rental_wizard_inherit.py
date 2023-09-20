# -*- coding: utf-8 -*-

from odoo import models, fields, api
from hijri_converter import Hijri, Gregorian


class RentRentalWizardInherit(models.TransientModel):
    _inherit = 'rental.wizard'

    duration_unit = fields.Selection(
        [("hour", "Hours"), ("day", "Days"), ("week", "Weeks"), ("month", "Months"), ("year", "years")],
        string="Unit", required=True, compute="_compute_duration")

    def day_nums(self):
        return [(day, str(day)) for day in list(range(1, 31))]

    def month_names(self):
        return [(1, 'محرم - 1'), (2, 'صفر - 2'), (3, 'ربيع الاول - 3'), (4, 'ربيع  الاخر - 4'),
                (5, 'جمادي الاولي   - 5'), (6, 'جمادي الاخرة   - 6'),
                (7, 'رجب - 7'), (8, 'شعبان -8'), (9, 'رمضان - 9'), (10, 'شوال - 10'), (11, 'ذو القعدة- 11'),
                (12, 'ذو الحجة - 12'),
                ]

    def get_year_range(self):
        found = self.env['hijri.year.range'].search([], limit=1)
        if found:
            return list(range(found.start_year, found.end_year + 1))

    def year_nums(self):
        hijri_range = self.get_year_range()
        if hijri_range:
            return [(year, str(year)) for year in hijri_range]
        else:
            return []

    hijri_pickup_day = fields.Selection(selection=day_nums)
    hijri_pickup_month = fields.Selection(selection=month_names)
    hijri_pickup_year = fields.Selection(selection=year_nums)

    hijri_return_day = fields.Selection(selection=day_nums)
    hijri_return_month = fields.Selection(selection=month_names)
    hijri_return_year = fields.Selection(selection=year_nums)

    @api.onchange('hijri_pickup_day', 'hijri_pickup_month','hijri_pickup_year')
    def _change_pickup_date(self):
        for rec in self:
            if rec.hijri_pickup_day and rec.hijri_pickup_month and rec.hijri_pickup_year:
                #get gregorian date correspond. to hijri date
                gregorian = Hijri(rec.hijri_pickup_year,rec.hijri_pickup_month,rec.hijri_pickup_day).to_gregorian()
                rec.pickup_date = rec.pickup_date.replace(day=gregorian.day, month=gregorian.month,
                                                          year=gregorian.year)

    @api.onchange('hijri_return_day', 'hijri_return_month','hijri_return_year')
    def _change_return_date(self):
        for rec in self:
            if rec.hijri_return_day and rec.hijri_return_month and rec.hijri_return_year:
                #get gregorian date correspond. to hijri date
                gregorian = Hijri(rec.hijri_return_year,rec.hijri_return_month,rec.hijri_return_day).to_gregorian()
                rec.return_date = rec.return_date.replace(day=gregorian.day, month=gregorian.month,
                                                          year=gregorian.year)

