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
            orders = rec.env['account.move.line'].search(
                [('move_id.move_type', '=', 'entry')])
            print(orders)
            for line in orders:
                lines.append({
                    'account': line.account_id.name,
                    'debit': line.debit,
                    'credit': line.credit
                })
            for order in orders:
                for order_item in order.account_id:
                    if order_item.id in lines_dict:
                        lines_dict[order_item.id] += order.debit
                        lines_dict[order_item.id] += order.credit
                        # product_dict[order_item.id].append(order.price_unit)
                    else:
                        lines_dict[order_item.id] = order.debit
                        lines_dict[order_item.id] = order.credit
            print(lines_dict)