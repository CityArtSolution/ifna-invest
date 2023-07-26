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
        accounts=[]
        lines_dict = {}
        for rec in self:
            if rec.move_type == 'entry':
                lines_dict = rec.env['account.move.line'].read_group(domain=[('move_id', '=', rec.id)],
                                                                     fields=['account_id','analytic_account_id',
                                                                             'credit', 'debit'],
                                                                     groupby=['account_id','analytic_account_id'],lazy=False,)
            print(lines_dict)
            for line in lines_dict:
                # print('debit', line.get('debit'))
                # print('credit', line.get('credit'))
                if line.get('debit') > line.get('credit'):
                    accounts.append(
                        {
                            line.get('account_id'):line.get('debit')
                        }
                    )
                else:
                    accounts.append(
                        {
                            line.get('account_id'): line.get('credit')
                        }
                    )
            print('accountssss',accounts)
            return lines_dict
