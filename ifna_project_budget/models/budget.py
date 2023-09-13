from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class AccountBudget(models.Model):
    _inherit = 'crossovered.budget'

    check_account = fields.Boolean(compute='action_get_account_info')

    @api.depends('crossovered_budget_line')
    def action_get_account_info(self):
        for rec in self:
            rec.check_account = False
            for line in rec.crossovered_budget_line:
                line.get_account_info()


class AccountLineBudget(models.Model):
    _inherit = 'crossovered.budget.lines'

    account_id = fields.Many2one(comodel_name="account.account", string='Account', compute="get_account_info",
                                 store=True)
    account_group_id = fields.Many2one(comodel_name="account.group", string='Account Group',
                                       compute="get_account_info", store=True)

    # @api.depends('general_budget_id')
    def get_account_info(self):
        for rec in self:
            rec.account_id = False
            rec.account_group_id = False
            if rec.general_budget_id:
                if rec.general_budget_id.account_ids:
                    rec.account_id = rec.general_budget_id.account_ids[0].id
                    rec.account_group_id = rec.general_budget_id.account_ids[0].group_id.id

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
                    if rec.crossovered_budget_id.state in ['confirm', 'validate', 'done']:
                        if account.user_type_id.internal_group in 'expense':
                            rec.deviation_value = rec.planned_amount + rec.practical_amount
                        if account.user_type_id.internal_group in 'income':
                            rec.deviation_value = rec.practical_amount - rec.planned_amount
                        # else:
                        #     rec.deviation_value = 0.0

    @api.depends('planned_amount', 'deviation_value')
    # @api.onchange('planned_amount', 'deviation_value')
    def _set_deviation_ratio(self):
        for rec in self:
            if rec.deviation_ratio or not rec.deviation_ratio:
                if rec.crossovered_budget_id.state in ['confirm', 'validate', 'done']:
                    if rec.deviation_value and rec.planned_amount > 0:
                        rec.deviation_ratio = (rec.deviation_value / rec.planned_amount)

    deviation_value = fields.Float(string="Deviation Value", compute='_set_deviation_value', default=0.0)
    deviation_ratio = fields.Float(string="Deviation Ratio", compute='_set_deviation_ratio', default=0.0)
    account_ids = fields.Many2many(comodel_name="account.account", string="Budgetary Account",
                                   related="general_budget_id.account_ids", )
