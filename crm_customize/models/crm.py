# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CRMLeadInherit(models.Model):
    _inherit = "crm.lead"
    property = fields.Many2one('rent.property', string='Property')

