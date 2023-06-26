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
class UtmMixinInherit(models.AbstractModel):
    _inherit = 'utm.mixin'

    source_id = fields.Many2one('utm.source', 'Customer Classification',
                                help="This is the source of the link, e.g. Search Engine, another domain, or name of email list")