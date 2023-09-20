# -*- coding: utf-8 -*-

from odoo import models, fields, api


class hijri_year_range(models.Model):
    _name = 'hijri.year.range'

    start_year = fields.Integer()
    end_year = fields.Integer()
