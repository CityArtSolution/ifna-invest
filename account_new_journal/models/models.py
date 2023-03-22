# -*- coding: utf-8 -*-

import time
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from itertools import groupby


class Journal(models.Model):
    _inherit = 'account.move'

    def calculate_total_account(self):
        lines_dict = {}
        dataaa = []
        lines = []
        for rec in self:
            if rec.move_type == 'entry':
                for line in rec.line_ids:
                    lines.append({
                        line.account_id.name:line.debit + line.credit,
                        # line.account_id.name:[line.debit + line.credit,line.analytic_account_id.name]
                        line.analytic_account_id.name:''
                    })
                for order in lines:
                    for item in order:
                        if item in lines_dict :
                            lines_dict[item] += order[item]
                            if item[1:] in lines_dict:
                                lines_dict[item] += order[item]
                                lines_dict[item].append(item.analytic_account_id)
                        else:
                            lines_dict[item] = order[item]
                            # lines_dict[item.analytic_account_id] = order[item.analytic_account_id]

                print(lines_dict)
                return lines_dict








# {'Current Assets': 100.0, 'تـأمين': account.analytic.account(21,),
#  'Account Receivable (PoS)': 100.0, 'رسوم ادارية': account.analytic.account(19,),
#  'Bank': 200.0, 'رسوم ادارية خاضعة': account.analytic.account(23,)}

# {'Current Assets': 300.0, 'تـأمين': account.analytic.account(21, 21),
# 'Account Receivable (PoS)': 100.0, 'رسوم ادارية': account.analytic.account(19,),
# 'Bank': 200.0, 'رسوم ادارية خاضعة': account.analytic.account(23,)}
