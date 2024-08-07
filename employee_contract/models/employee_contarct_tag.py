# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EmployeeContract(models.Model):
    _name = 'employee.contract.tag'
    _description = "IFNA Employee Contract Tag"

    active = fields.Boolean(default=True)
    name = fields.Char(tracking=True, required=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company.id,
                                 tracking=True)
    color = fields.Integer(tracking=True, default=lambda self: self._default_color())

    def _default_color(self):
        return 0
