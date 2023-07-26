# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class crm_extend(models.Model):
    _inherit = 'crm.lead'

    property = fields.Many2one('rent.property', string='العقار')
    unit = fields.Many2one('product.template', string='الوحدة', domain="[('property_id', '=', property)]")
    date = fields.Date("Date")
    source_id = fields.Many2one('utm.source', 'تصنيف العميل',
                                help="This is the source of the link, e.g. Search Engine, another domain, or name of email list")

    @api.depends('unit')
    def _compute_name(self):
        for lead in self:
            if lead.unit and lead.unit.name:
                lead.name = _("%s's opportunity") % lead.unit.name
