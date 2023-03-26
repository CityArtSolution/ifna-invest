# -*- coding: utf-8 -*-

import time
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class NewModule(models.Model):
    _inherit = 'account.move.line'

    # def samah(self):
    #     accounts = self.env['account.analytic.account']
    #     for line in self:
    #         if '__domain' in line:
    #             accounts = self.search(line['__domain'])
    #         if 'debit' in fields:
    #             line['debit'] = sum(accounts.mapped('debit'))
    #         if 'credit' in fields:
    #             line['credit'] = sum(accounts.mapped('credit'))
    #         print(line)

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                          index=True, compute="_compute_analytic_account_id", store=True,
                                          readonly=False,
                                          check_company=True, copy=True)
    new_analytic_account_id = fields.Many2one('account.analytic.account', related='analytic_account_id', )


class Journal(models.Model):
    _inherit = 'account.move'

    def calculate_total_account(self):
        lines_dict = {}
        for rec in self:
            if rec.move_type == 'entry':
                lines_dict = rec.env['account.move.line'].read_group(domain=[('move_id', '=', rec.id)],
                                                                     fields=['account_id','analytic_account_id',
                                                                             'credit', 'debit'],
                                                                     groupby=['account_id','analytic_account_id'],lazy=False,)

                new = rec.env['account.move.line'].read_group(domain=[('move_id', '=', rec.id)],
                                                              fields=['analytic_account_id', 'debit', 'credit'],
                                                              groupby=['analytic_account_id'])

            print('lines', lines_dict)
            print('new', new)
            for line in lines_dict:
                print('account', line.get('account_id'))
                print('account analytic', line.get('analytic_account_id'))
            return lines_dict

    # def calculate_total_account(self):
    #     lines_dict = {}
    #     dataaa = []
    #     lines = []
    #     for rec in self:
    #         if rec.move_type == 'entry':
    #             for line in rec.line_ids:
    #                 lines.append({
    #                     line.account_id.name:line.debit + line.credit,
    #                     # line.account_id.name:[line.debit + line.credit,line.analytic_account_id.name]
    #                     line.analytic_account_id.name:''
    #                 })
    #             for order in lines:
    #                 for item in order:
    #                     if item in lines_dict :
    #                         # lines_dict[item] += order[item]
    #                         # if item[1:] in lines_dict:
    #                             lines_dict[item] += order[item]
    #                             # lines_dict[item].append(item.analytic_account_id)
    #                     else:
    #                         lines_dict[item] = order[item]
    #                         # lines_dict[item.analytic_account_id] = order[item.analytic_account_id]
    #
    #             print(lines_dict)
    #             return lines_dict

