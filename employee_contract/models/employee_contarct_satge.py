# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EmployeeContract(models.Model):
    _name = 'employee.contract.stage'
    _description = "IFNA Employee Contract Stage"

    active = fields.Boolean(default=True)
    name = fields.Char(tracking=True, required=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company.id,
                                 tracking=True)
    sequence = fields.Integer(tracking=True)
