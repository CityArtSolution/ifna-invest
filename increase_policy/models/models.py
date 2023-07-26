# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class IncreasePolicy(models.Model):
    _name = "increase.policy"

    name = fields.Char(string="Policy Sequence")

    date_from = fields.Datetime(string="من")
    date_to = fields.Datetime(string="إلى")
    desc = fields.Html(string="وصف الإتفاق")
    invoice_number = fields.Integer(string='Number Of Invoices')
    line_sequence = fields.Char(string="Line Sequence", store=True, compute="compute_lines")

    orders_count = fields.Integer(compute="get_orders")

    line_ids = fields.One2many("increase.policy.line", 'line_id')

    @api.depends('line_ids')
    def compute_lines(self):
        for record in self:
            lines = record.line_ids
            count = 1
            for i in lines:
                i.seq = " رقم " + str(count)
                i.year = count
                count = count + 1
                record.line_sequence = i.id

    def get_orders(self):
        for rec in self:
            orders = self.env['sale.order.line'].search([('increase_policy', '=', rec.id)]).mapped('order_id')
            rec.orders_count = len(orders)

    def rental_order(self):
        for rec in self:
            orders = self.env['sale.order.line'].search([('increase_policy', '=', rec.id)]).mapped('order_id')
            orders_ids = []
            for each in orders:
                orders_ids.append(each.id)
            view_id = self.env.ref('sale_renting.rental_order_primary_form_view').id
            view_id_tree = self.env.ref('sale_renting.rental_order_view_tree').id
            if orders_ids:
                if len(orders_ids) <= 1:
                    value = {
                        'view_mode': 'form',
                        'res_model': 'sale.order',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Rental Order'),
                        'res_id': orders_ids and orders_ids[0],
                    }
                else:
                    value = {
                        'domain': str([('id', 'in', orders_ids)]),
                        'view_mode': 'tree,form',
                        'view_type': 'form',
                        'res_model': 'sale.order',
                        # 'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Rental Order'),
                        'context': {'default_is_rental_order': 1, 'search_default_from_rental': 1}
                    }
                return value

    @api.onchange('date_from', 'date_to')
    def get_period(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                total_contract_period = rec.date_to - rec.date_from
                if total_contract_period.days <= 0:
                    raise UserError(_('يجب اختيار مدة العقد بصورة صحيحة'))

                todate = rec.date_to + relativedelta(days=1)
                diff = relativedelta(todate, rec.date_from)
                rec.invoice_number = diff.years+1

                if rec.line_ids:
                    rec.line_ids.unlink()
                else:
                    for i in range(0, rec.invoice_number):
                        self.env['increase.policy.line'].create({
                            'seq': "فاتورة رقم " + str(i+1),
                            'year': i + 1,
                            'line_id': rec.id,
                        })


class IncreasePolicyLine(models.Model):
    _name = "increase.policy.line"

    line_id = fields.Many2one("increase.policy")

    year = fields.Char("السنة")
    seq = fields.Char("Seq")
    type = fields.Selection([('percent', 'Percent'), ('value', 'Value')], default="value", string="Increase Type")
    percent = fields.Integer("Percent")
    value = fields.Float("Value")
