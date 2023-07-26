# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class CRMPartnerIndustry(models.Model):
    _inherit = 'crm.lead'

    industry_id = fields.Many2one('res.partner.industry', 'Customer Industry', readonly=False,
                                  related="partner_id.industry_id")
