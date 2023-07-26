# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IncreasePolicy(models.TransientModel):
    _inherit = "res.config.settings"

    module_increase_policy = fields.Boolean(string="Increase Policy")

