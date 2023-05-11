# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CRMLeadInherit(models.Model):
    _inherit = "crm.lead"
    property = fields.Many2one('rent.property', string='Property')
    product_id = fields.Many2one(
        'product.product', string='Unit', change_default=True, ondelete='restrict', check_company=True)
    property_date = fields.Date(string="Date", required=False, )

    @api.onchange('product_id')
    def get_unit_name_into_lead_name(self):
        if self.product_id:
            self.name = self.product_id.name
