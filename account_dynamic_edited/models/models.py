# -*- coding: utf-8 -*-

import time
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class AccountGroupInherit(models.Model):
    _inherit = 'account.group'

    level_id = fields.Many2one(comodel_name="account.group.level", string="Level")

    # @api.constrains('level_id')
    # def _check_same_level(self):
    #     if self.level_id:
    #         groups = self.env['account.group'].search([('id', '!=', self.id)])
    #         for record in groups:
    #             if record.level_id:
    #                 if record.level_id == self.level_id:
    #                     raise ValidationError("This Level already related with another Account Group !")


class AccountGroupLevel(models.Model):
    _name = 'account.group.level'
    _rec_name = 'name'

    name = fields.Integer(string="Level")
    parent_id = fields.Many2one(comodel_name="account.group.level", string="Parent")

    @api.constrains('parent_id')
    def _check_same_parent(self):
        if self.parent_id:
            levels = self.env['account.group.level'].search([('id', '!=', self.id)])
            for record in levels:
                if record.parent_id:
                    if record.parent_id == self.parent_id:
                        raise ValidationError("This Parent already related with another Level !")

    _sql_constraints = [
        ('unique_name', 'unique (name)', "You can't create an Level with an existing Number, Please change it.")
    ]


class Journal(models.Model):
    _inherit = 'account.move'

    def calculate_total_account(self):
        lines_dict = {}
        for rec in self:
            if rec.move_type == 'entry':
                lines_dict = rec.env['account.move.line'].read_group(domain=[('move_id', '=', rec.id)],
                                                                     fields=['account_id', 'analytic_account_id',
                                                                             'credit', 'debit'],
                                                                     groupby=['account_id', 'analytic_account_id'])
            # print('lines', lines_dict)
            # for line in lines_dict:
            #     print('account',line.get('account_id')[0])
            #     print('account analytic',line.get('analytic_account_id'))
            return lines_dict

    # def calculate_total_account(self):
    #     lines_dict = {}
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
    #                         lines_dict[item] += order[item]
    #                         if item[1:] in lines_dict:
    #                             lines_dict[item] += order[item]
    #                             lines_dict[item].append(item.analytic_account_id)
    #                     else:
    #                         lines_dict[item] = order[item]
    #                         # lines_dict[item.analytic_account_id] = order[item.analytic_account_id]
    #
    #             print(lines_dict)
    #             return lines_dict
