from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class AccountBudget(models.Model):
    _inherit = 'crossovered.budget'


class AccountLineBudget(models.Model):
    _inherit = 'crossovered.budget.lines'

    @api.depends('planned_amount','practical_amount')
    @api.onchange('planned_amount','practical_amount')
    def _set_deviation_value(self):
        for rec in self:
            for account in rec.general_budget_id.account_ids:
                if account.user_type_id.internal_group in 'expense':
                    print(account)
                    rec.deviation_value = rec.planned_amount + rec.practical_amount
                    print(rec.deviation_value)
                elif account.user_type_id.internal_group in 'income' :
                    rec.deviation_value =  rec.practical_amount - rec.planned_amount
                else:
                    rec.deviation_value = 0.0

    @api.depends('planned_amount','deviation_value')
    @api.onchange('planned_amount','deviation_value')
    def _set_deviation_ratio(self):
        for rec in self:
            if rec.deviation_value:
                rec.deviation_ratio = rec.planned_amount / rec.deviation_value
    # @api.multi
    # def write(self, values):
    #     # Add code here
    #     self._set_deviation_value()
    #     self._set_deviation_ratio()
    #     return super(AccountLineBudget, self).write(values)

    deviation_value = fields.Float(string="Deviation Value", compute='_set_deviation_value',store=True )
    deviation_ratio = fields.Float(string="Deviation Ratio",  compute='_set_deviation_ratio',store=True )
    account_ids = fields.Many2many(comodel_name="account.account", string="Budgetary Account", related="general_budget_id.account_ids", )
