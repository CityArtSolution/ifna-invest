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