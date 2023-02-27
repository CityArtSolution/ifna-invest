from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class AccountBudget(models.Model):
    _inherit = 'crossovered.budget'


class AccountLineBudget(models.Model):
    _inherit = 'crossovered.budget.lines'

    def _compute_practical_amount(self):
        for line in self:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', line.analytic_account_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]

                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause

            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           line.general_budget_id.account_ids.ids),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('move_id.state', '=', 'posted')
                          ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.practical_amount = self.env.cr.fetchone()[0] or 0.0
        # self._set_deviation_value()
        # self._set_deviation_ratio()

    @api.depends('planned_amount', 'practical_amount')
    # @api.onchange('planned_amount', 'practical_amount')
    def _set_deviation_value(self):
        for rec in self:
            for account in rec.general_budget_id.account_ids:
                if rec.deviation_value or not rec.deviation_value:
                    if rec.crossovered_budget_id.state in ['confirm','validate','done']:
                        if account.user_type_id.internal_group in 'expense':
                            print(account)
                            rec.deviation_value = rec.planned_amount + rec.practical_amount
                            print(rec.deviation_value)
                        if account.user_type_id.internal_group in 'income':
                            rec.deviation_value = rec.practical_amount - rec.planned_amount
                        # else:
                        #     rec.deviation_value = 0.0

    @api.depends('planned_amount', 'deviation_value')
    # @api.onchange('planned_amount', 'deviation_value')
    def _set_deviation_ratio(self):
        for rec in self:
            if rec.deviation_ratio or not rec.deviation_ratio:
                if rec.crossovered_budget_id.state in ['confirm','validate','done']:
                    if rec.deviation_value and rec.planned_amount > 0:
                        rec.deviation_ratio = (rec.deviation_value /rec.planned_amount)

    deviation_value = fields.Float(string="Deviation Value", compute='_set_deviation_value',default=0.0 )
    deviation_ratio = fields.Float(string="Deviation Ratio", compute='_set_deviation_ratio',default=0.0  )
    account_ids = fields.Many2many(comodel_name="account.account", string="Budgetary Account",
                                   related="general_budget_id.account_ids", )