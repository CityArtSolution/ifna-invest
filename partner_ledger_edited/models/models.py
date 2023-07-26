# -*- coding: utf-8 -*-

import time
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class Journal(models.Model):
    _inherit = 'account.move'

    def calculate_total_account(self):
        lines_dict = {}
        for rec in self:
            if rec.move_type == 'entry':
                lines_dict = rec.env['account.move.line'].read_group(domain=[('move_id', '=', rec.id)],
                                                                     fields=['account_id', 'analytic_account_id',
                                                                             'credit', 'debit'],
                                                                     groupby=['account_id', 'analytic_account_id'],
                                                                     lazy=False, )

            # if lines_dict:
            return lines_dict
