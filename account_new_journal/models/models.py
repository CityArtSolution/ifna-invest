# -*- coding: utf-8 -*-

import time
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class Journal(models.Model):
    _inherit = 'account.move'

    def calculate_total_account(self):
        lines_dict = {}
        lines = []
        for rec in self:
            if rec.move_type == 'entry':
                for line in rec.line_ids:
                    lines.append({
                         line.account_id:line.debit + line.credit,
                    })
                print(lines)
                for order in lines:
                    for item in order:
                        if item in lines_dict:
                            lines_dict[item] += order[item]
                        else:
                            lines_dict[item] = order[item]
                print(lines_dict)
            return lines_dict
