# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class RentSaleOrder(models.Model):
    _inherit = 'sale.order'

    increase_policy_lines = fields.Many2many("increase.policy", string="Increase Policy")

    def create_order_invoices(self):
        for rec in self:
            if rec.invoice_number <= 0:
                raise UserError(_('من فضلك اكتب عدد الفواتير'))
            rec.order_contract_invoice = False
            fromdate = rec.fromdate
            d1 = fields.Datetime.from_string(rec.fromdate)
            d2 = fields.Datetime.from_string(rec.todate)
            total_contract_period = d2 - d1

            if total_contract_period.days <= 0:
                raise UserError(_('يجب اختيار مدة العقد بصورة صحيحة'))

            diff = 0
            diff = total_contract_period.days / rec.invoice_number
            diff = round(diff, 0)
            # if abs(total_contract_period.days) % abs(rec.invoice_number) >0:
            #     raise UserError(_('يجب كتابة عدد فواتير مناسب لمدة العقد'))
            #

            separate = False
            for s in rec.order_line:
                if s.product_id.product_tmpl_id.separate:
                    separate = True
                    break
            if separate:
                lines = rec.order_line.filtered(lambda s: s.product_id.product_tmpl_id.separate == True)
                amount = sum(lines.mapped('price_subtotal')) - sum(lines.mapped('increase_amount'))
                services = lines.mapped('product_id')

                sale_invoices = self.env['rent.sale.invoices'].create({
                    'name': "فاتورة رقم " + "0",
                    'sequence': 0,
                    'separate': True,
                    'fromdate': fromdate,
                    'invoice_date': fromdate.date(),
                    'todate': rec.todate,
                    'amount': amount,
                    'sale_order_id': rec.id,
                    'services': services,
                })
            for i in range(0, rec.invoice_number + 1):
                if separate:
                    products = rec.order_line.filtered(
                        lambda s: s.product_id.product_tmpl_id.separate == False).mapped('product_id')
                    total_other_amount = sum((
                                                     i.insurance_value + i.contract_admin_fees + i.contract_service_fees + i.contract_admin_sub_fees + i.contract_service_sub_fees)
                                             for i in rec.order_line.filtered(
                        lambda s: s.product_id.product_tmpl_id.separate == False))
                    taxed_total_other_amount = sum(
                        (i.contract_admin_sub_fees + i.contract_service_sub_fees) for i in
                        rec.order_line.filtered(lambda s: s.product_id.product_tmpl_id.separate == False))

                    total_property_amount_without_tax = sum(
                        (i.product_uom_qty * (i.price_unit - i.increase_amount)) for i in
                        rec.order_line.filtered(lambda
                                                    s: s.product_id.product_tmpl_id.separate == False))

                    property_amount_per_inv = total_property_amount_without_tax / rec.invoice_number

                    total_tax_first_inv = sum(
                        (property_amount_per_inv + taxed_total_other_amount) * (tax.amount / 100) for tax in
                        rec.order_line.filtered(lambda s: s.product_id.product_tmpl_id.separate == False).tax_id)
                    total_tax = sum((property_amount_per_inv) * (tax.amount / 100) for tax in rec.order_line.tax_id)
                else:
                    products = rec.order_line.mapped('product_id')
                    total_other_amount = sum((
                                                     i.insurance_value + i.contract_admin_fees + i.contract_service_fees + i.contract_admin_sub_fees + i.contract_service_sub_fees)
                                             for i in rec.order_line)
                    taxed_total_other_amount = sum(
                        (i.contract_admin_sub_fees + i.contract_service_sub_fees) for i in rec.order_line)

                    total_property_amount_without_tax = sum(
                        (i.product_uom_qty * (i.price_unit - i.increase_amount)) for i in rec.order_line)

                    property_amount_per_inv = total_property_amount_without_tax / rec.invoice_number

                    total_tax_first_inv = sum(
                        (property_amount_per_inv + taxed_total_other_amount) * (tax.amount / 100) for tax in
                        rec.order_line.tax_id)
                    total_tax = sum((property_amount_per_inv) * (tax.amount / 100) for tax in rec.order_line.tax_id)

                if rec.invoice_terms == "monthly":
                    todate = fromdate + relativedelta(months=1) - relativedelta(days=1)
                if rec.invoice_terms == "quarterly":
                    todate = fromdate + relativedelta(months=3) - relativedelta(days=1)
                if rec.invoice_terms == "semi":
                    todate = fromdate + relativedelta(months=6) - relativedelta(days=1)
                if rec.invoice_terms == "yearly":
                    todate = fromdate + relativedelta(years=1) - relativedelta(days=1)

                if i == 1:
                    amount = property_amount_per_inv + total_other_amount + total_tax_first_inv
                if i == rec.invoice_number:
                    amount = total_property_amount_without_tax - sum(rec.order_contract_invoice.mapped('amount'))
                else:
                    amount = property_amount_per_inv + total_tax
                if amount > 0:
                    sale_invoices = self.env['rent.sale.invoices'].create({
                        'name': "فاتورة رقم " + str(i + 1),
                        'sequence': i,
                        'fromdate': fromdate,
                        'invoice_date': fromdate.date(),
                        'todate': rec.todate if rec.invoice_number == i else todate,
                        'amount': amount,
                        'sale_order_id': rec.id,
                        'services': products,
                    })
                fromdate = todate + relativedelta(days=1)

    def increase_policy(self):
        for rec in self:
            for i in rec.order_line.filtered(lambda x: x.product_id.rent_ok == True):
                price = i.price_unit
                increase_amount = 0
                if i.increase_policy:
                    for j in i.increase_policy.line_ids:
                        if j.type == 'percent':
                            percent = price * j.percent / 100
                            price = price + percent
                            increase_amount = increase_amount + percent
                        if j.type == 'value':
                            price = price + j.value
                            increase_amount = increase_amount + j.value
                    i.increase_amount = increase_amount
                    i.price_unit = price

    @api.onchange('fromdate', 'todate')
    def get_increase_policy(self):
        lines = self.env['increase.policy'].search(
            [('date_from', '>=', self.fromdate), ('date_from', '<=', self.todate), ('date_to', '<=', self.todate),
             ('date_to', '>=', self.fromdate)])
        # self.increase_policy = lines.ids
        self.increase_policy_lines = [(6, 0, lines.ids)]
        # self.order_line.get_increase_policy()
        # return {'domain': {'order_line.increase_policy': [('id', 'in', self._origin.order_id.increase_policy_lines.ids)]}}


class RentSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # @api.onchange('increase_policy')
    # @api.model

    # increase_policy = fields.Many2one("increase.policy", string="Increase Policy", domain=lambda self: [('id', 'in', self.order_id.increase_policy_lines.ids)])
    # increase_policy = fields.Many2one("increase.policy", string="Increase Policy", domain=lambda self: self._domain_increase_policy())
    increase_policy = fields.Many2one("increase.policy", string="Increase Policy")
    increase_amount = fields.Float(string="Increase Amount")

    @api.onchange('increase_policy')
    def domain_increase_policy(self):
        print("........................",self.order_id.increase_policy_lines)
        print(".................,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,........",self._origin.order_id.increase_policy_lines)
        if self.order_id.increase_policy_lines:
            return {'domain': {'increase_policy': [('id', 'in', self.order_id.increase_policy_lines.ids)]}}
        # else:
        # return False
