# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError

INSURANCE_ADMIN_FEES_FIELDS = ['insurance_value', 'contract_admin_fees', 'contract_service_fees',
                               'contract_admin_sub_fees', 'contract_service_sub_fees']

from hijri_converter import Hijri, Gregorian


class ConfigurationSettings(models.TransientModel):
    _inherit = "res.config.settings"

    separate = fields.Boolean(string="Separate Invoice for Additional Services")


class UpdatedInvoice(models.Model):
    _name = 'updated.invoice'

    name = fields.Char(string='name')


class RentSaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_number = fields.Char(readonly=True, string='رقم العقد')
    fromdate = fields.Datetime(string='From Date', default=datetime.today(), copy=False, required=True)
    todate = fields.Datetime(string='To Date', default=datetime.today(), copy=True, required=True)
    # Fields in Contract Info Tab
    order_contract = fields.Binary(string='العقد')
    invoice_terms = fields.Selection(
        [('monthly', 'monthly'), ('quarterly', 'quarterly'), ('semi', 'Semi'), ('yearly', 'yearly')],
        string='Invoice Terms',
        default='monthly')
    ejar = fields.Selection([('ejar', 'EJAR')], string='EJAR')
    ejar_number = fields.Char(string='EJAR Contract Number')
    ejar_date = fields.Datetime(string='EJAR Contract Date')
    remarks_c = fields.Char(string='Remarks (Contract)')
    file = fields.Selection([('yes', 'yes'), ('no', 'No')], string='File Completed', default='no')
    updated_invoice = fields.Selection([('updated', 'Updated'), ('invoiced', 'Invoiced')], string='Updated Invoiced')
    updated_invoices = fields.Many2one("updated.invoice", string='Updated Invoiced')
    order_contract_invoice = fields.One2many('rent.sale.invoices', 'sale_order_id', string='العقد')
    contract_total_payment = fields.Float(string='Total Contract')
    contract_total_fees = fields.Float(string='Total Fees')
    brand_nameplate_allowed = fields.Boolean(string='Nameplate Allowed')
    contract_hegira_date = fields.Char(string='التاريخ الهجري')
    contract_penalties = fields.Float(string='الجزائات')
    contract_extra_maintenance_cost = fields.Float(string='تكلفة الصيانة الاضافية')
    contractor_pen = fields.Char(string='رسوم متأخرات')
    amount_remain = fields.Float(string='اجمالي المتبقي', compute='_get_remain')
    invoice_number = fields.Integer(string='Number Of Invoices')
    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                 auto_join=True)

    order_property_state = fields.One2many('rent.sale.state', 'sale_order_id', string='الحالة')

    # بنود الاستلام
    door_good = fields.Boolean('جيد')
    door_bad = fields.Boolean('سئ')
    door_comment = fields.Char('حدد')
    wall_good = fields.Boolean('جيد')
    wall_bad = fields.Boolean('سئ')
    wall_comment = fields.Char('حدد')
    window_good = fields.Boolean('جيد')
    window_bad = fields.Boolean('سئ')
    window_comment = fields.Char('حدد')
    water_good = fields.Boolean('جيد')
    water_bad = fields.Boolean('سئ')
    water_comment = fields.Char('حدد')
    elec_good = fields.Boolean('جيد')
    elec_bad = fields.Boolean('سئ')
    elec_comment = fields.Char('حدد')
    rdoor_good = fields.Boolean('جيد')
    rdoor_bad = fields.Boolean('سئ')
    rdoor_comment = fields.Char('حدد')
    rwall_good = fields.Boolean('جيد')
    rwall_bad = fields.Boolean('سئ')
    rwall_comment = fields.Char('حدد')
    rwindow_good = fields.Boolean('جيد')
    rwindow_bad = fields.Boolean('سئ')
    rwindow_comment = fields.Char('حدد')
    rwater_good = fields.Boolean('جيد')
    rwater_bad = fields.Boolean('سئ')
    rwater_comment = fields.Char('حدد')
    relec_good = fields.Boolean('جيد')
    relec_bad = fields.Boolean('سئ')
    relec_comment = fields.Char('حدد')
    customer_accept = fields.Boolean('نعم')
    customer_refused = fields.Boolean('لا')
    notes = fields.Text('الملاحظات')
    rnotes = fields.Text('الملاحظات')
    mangement_accept = fields.Boolean('نعم')
    mangement_refused = fields.Boolean('لا')
    manage_note = fields.Text('ملاحظة')
    rmanage_note = fields.Text('ملاحظة')
    is_cost = fields.Boolean('نعم')
    is_no_cost = fields.Boolean('لا')
    is_amount_rem = fields.Boolean('نعم')
    is_no_amount_rem = fields.Boolean('لا')
    amount_rem = fields.Float('المبلغ المتبقي')
    iselec_remain = fields.Boolean('نعم')
    isnotelec_remain = fields.Boolean('لا')

    is_pm = fields.Boolean('is PM', compute="_get_if_group")
    is_finance = fields.Boolean('is Finance', compute="_get_if_group")

    @api.model
    def create(self, vals):
        result = super(RentSaleOrder, self).create(vals)
        result.contract_number = "Contract/" + str(fields.Date.today().year) + "/" + str(
            fields.Date.today().month) + "-" + "000" + str(result.id)
        if result.invoice_number <= 0 and result.is_rental_order:
            raise UserError(_('من فضلك اكتب عدد الفواتير'))
        return result

    @api.depends('partner_id')
    def _get_if_group(self):
        for rec in self:
            rec.is_pm = False
            rec.is_finance = False
            if self.user_has_groups('renting_workflow_customization.pm_group'):
                rec.is_pm = True
            if self.user_has_groups('renting_workflow_customization.finance_group'):
                rec.is_finance = True

    @api.model
    def create_invoices_cron(self):
        for i in self.env['sale.order'].search([]):
            if i.order_contract_invoice:
                for rec in i.order_contract_invoice:
                    if rec.invoice_date <= fields.Date.today() and rec.status == "uninvoiced":
                        invoice_lines = []
                        invoiceable_lines = rec.sale_order_line_ids
                        # if rec.sequence == 1:
                        #     seq = 0
                        #     for type in INSURANCE_ADMIN_FEES_FIELDS:
                        #         seq += 1
                        #         fees_sum = rec._prepare_invoice_line_insurance_admin_fees_sum(type, seq)
                        #         if fees_sum.get('name', False):
                        #             invoice_lines.append([0, 0, fees_sum])
                        for line in invoiceable_lines:
                            invoice_lines.append([0, 0, rec._prepare_invoice_line(line)])
                            # if rec.sequence == 1:
                            #     seq = 0
                            #     for type in INSURANCE_ADMIN_FEES_FIELDS:
                            #         seq += 1
                            #         if line.mapped(type)[0] > 0:
                            #             invoice_lines.append(
                            #                 [0, 0, rec._prepare_invoice_line_insurance_admin_fees(type, line, seq)])
                        print(invoice_lines)

                        vals = rec._prepare_invoice(invoice_lines)
                        invoice = self.env['account.move'].create(vals)
                        # rec.invoice_date = fields.Date.today()
                        rec.status = 'invoiced'

    def action_pickup(self):
        self.write({'rental_status': 'return'})

    def _get_remain(self):
        amount = 0
        invoices_paid = self.env['account.move'].sudo().search(
            [('invoice_origin', '=', self.name), ('payment_state', 'in', ['paid', 'in_payment'])])
        for line in invoices_paid:
            print(line)
            amount += line.amount_total
        self.amount_remain = self.amount_total - amount

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    def create_order_invoices(self):
        for rec in self:
            if rec.order_contract_invoice:
                invoiced = rec.order_contract_invoice.filtered(lambda l: l.status == 'invoiced')
                if invoiced:
                    raise UserError(_('Invoices can not be Regenerated ,Some are Invoiced'))

            if rec.invoice_number <= 0:
                raise UserError(_('من فضلك اكتب عدد الفواتير'))
            rec.order_contract_invoice = False
            fromdate = rec.fromdate
            d1 = fields.Datetime.from_string(rec.fromdate)
            d2 = fields.Datetime.from_string(rec.todate)
            total_contract_period = d2 - d1
            if total_contract_period.days <= 0:
                raise UserError(_('يجب اختيار مدة العقد بصورة صحيحة'))

            # separate = False
            # for s in rec.order_line:
            #     if s.product_id.product_tmpl_id.separate:
            #         separate = True
            #         break

            year_amount = rec.order_line.read_group([('order_id', '=', rec.id)], ['price_subtotal:sum', 'product_id'],
                                                    'line_year_number')

            count = 0
            # for i in range(0, rec.todate.date().year-rec.fromdate.date().year):
            for amount in year_amount:
                sale_order_line_ids = rec.order_line.filtered(
                    lambda i: i.line_year_number == amount['line_year_number'])
                products = sale_order_line_ids.mapped('product_id')
                terms = 0
                if rec.invoice_terms == "monthly":
                    terms = 12
                if rec.invoice_terms == "quarterly":
                    terms = 4
                if rec.invoice_terms == "semi":
                    terms = 2
                if rec.invoice_terms == "yearly":
                    terms = 1

                for i in range(0, terms):
                    if rec.invoice_terms == "monthly":
                        todate = fromdate + relativedelta(months=1) - relativedelta(days=1)
                    if rec.invoice_terms == "quarterly":
                        todate = fromdate + relativedelta(months=3) - relativedelta(days=1)
                    if rec.invoice_terms == "semi":
                        todate = fromdate + relativedelta(months=6) - relativedelta(days=1)
                    if rec.invoice_terms == "yearly":
                        todate = fromdate + relativedelta(years=1) - relativedelta(days=1)
                    # if amount > 0:
                    sale_invoices = self.env['rent.sale.invoices'].create({
                        'name': "فاتورة رقم " + str(count + 1),
                        'sequence': count,
                        'fromdate': fromdate,
                        'invoice_date': fromdate.date(),
                        'todate': todate,
                        'amount': amount['price_subtotal'] / terms,
                        'sale_order_id': rec.id,
                        'sale_order_line_ids': sale_order_line_ids,
                        'services': products,
                    })
                    fromdate = todate + relativedelta(days=1)
                    count = count + 1

            # separate = False
            # for s in rec.order_line:
            #     if s.product_id.product_tmpl_id.separate:
            #         separate = True
            #         break
            # if separate:
            #     lines = rec.order_line.filtered(lambda s: s.product_id.product_tmpl_id.separate == True)
            #     amount = sum(lines.mapped('price_subtotal'))
            #     services = lines.mapped('product_id')
            #
            #     sale_invoices = self.env['rent.sale.invoices'].create({
            #         'name': "فاتورة رقم " + "0",
            #         'sequence': 0,
            #         'separate': True,
            #         'fromdate': fromdate,
            #         'invoice_date': fromdate.date(),
            #         'todate': rec.todate,
            #         'amount': amount,
            #         'sale_order_id': rec.id,
            #         'services': services,
            #     })
            # for i in range(0, rec.invoice_number + 1):
            #     if separate:
            #         products = rec.order_line.filtered(
            #             lambda s: s.product_id.product_tmpl_id.separate == False).mapped('product_id')
            #         total_other_amount = sum((i.insurance_value + i.contract_admin_fees + i.contract_service_fees + i.contract_admin_sub_fees + i.contract_service_sub_fees)
            #                                  for i in rec.order_line.filtered(
            #             lambda s: s.product_id.product_tmpl_id.separate == False))
            #         taxed_total_other_amount = sum(
            #             (i.contract_admin_sub_fees + i.contract_service_sub_fees) for i in
            #             rec.order_line.filtered(lambda s: s.product_id.product_tmpl_id.separate == False))
            #
            #         total_property_amount_without_tax = sum((i.product_uom_qty * i.price_unit) for i in
            #                                                 rec.order_line.filtered(lambda
            #                                                                             s: s.product_id.product_tmpl_id.separate == False))
            #
            #         property_amount_per_inv = total_property_amount_without_tax / rec.invoice_number
            #
            #         total_tax_first_inv = sum(
            #             (property_amount_per_inv + taxed_total_other_amount) * (tax.amount / 100) for tax in
            #             rec.order_line.filtered(lambda s: s.product_id.product_tmpl_id.separate == False).tax_id)
            #         total_tax = sum((property_amount_per_inv) * (tax.amount / 100) for tax in rec.order_line.tax_id)
            #     else:
            #
            #         total_other_amount = sum((
            #                                          i.insurance_value + i.contract_admin_fees + i.contract_service_fees + i.contract_admin_sub_fees + i.contract_service_sub_fees)
            #                                  for i in rec.order_line)
            #         taxed_total_other_amount = sum(
            #             (i.contract_admin_sub_fees + i.contract_service_sub_fees) for i in rec.order_line)
            #
            #         total_property_amount_without_tax = sum((i.product_uom_qty * i.price_unit) for i in rec.order_line)
            #
            #         property_amount_per_inv = total_property_amount_without_tax / rec.invoice_number
            #
            #         total_tax_first_inv = sum(
            #             (property_amount_per_inv + taxed_total_other_amount) * (tax.amount / 100) for tax in
            #             rec.order_line.tax_id)
            #         total_tax = sum((property_amount_per_inv) * (tax.amount / 100) for tax in rec.order_line.tax_id)
            #
            #
            #     if rec.invoice_terms == "monthly":
            #         todate = fromdate + relativedelta(months=1) - relativedelta(days=1)
            #     if rec.invoice_terms == "quarterly":
            #         todate = fromdate + relativedelta(months=3) - relativedelta(days=1)
            #     if rec.invoice_terms == "semi":
            #         todate = fromdate + relativedelta(months=6) - relativedelta(days=1)
            #     if rec.invoice_terms == "yearly":
            #         todate = fromdate + relativedelta(years=1) - relativedelta(days=1)
            #
            #     if i == 1:
            #         amount = property_amount_per_inv + total_other_amount + total_tax_first_inv
            #     if i == rec.invoice_number:
            #         amount = total_property_amount_without_tax - sum(rec.order_contract_invoice.mapped('amount'))
            #     else:
            #         amount = property_amount_per_inv + total_tax
            #
            #     products = rec.order_line.mapped('product_id')
            #     if amount > 0:
            #         sale_invoices = self.env['rent.sale.invoices'].create({
            #             'name': "فاتورة رقم " + str(i + 1),
            #             'sequence': i,
            #             'fromdate': fromdate,
            #             'invoice_date': fromdate.date(),
            #             'todate': rec.todate if rec.invoice_number == i else todate,
            #             'amount': amount,
            #             'sale_order_id': rec.id,
            #             'services': products,
            #         })
            #     fromdate = todate + relativedelta(days=1)

    @api.onchange("fromdate", "todate", "invoice_terms")
    def onchang_contract_dates(self):
        self.get_invoice_number()

    def get_invoice_number(self):
        for rec in self:
            todate = rec.todate + relativedelta(days=1)
            diff = relativedelta(todate, rec.fromdate)

            terms = 0
            if rec.invoice_terms == "monthly":
                terms = 12
            if rec.invoice_terms == "quarterly":
                terms = 4
            if rec.invoice_terms == "semi":
                terms = 2
            if rec.invoice_terms == "yearly":
                terms = 1
            rec.invoice_number = terms * diff.years
            #
            # todate = rec.todate + relativedelta(days=1)
            # diff = relativedelta(todate, rec.fromdate)
            # m = month = 0
            # if diff.years != 0:
            #     m = diff.years * 12
            # if diff.months != 0:
            #     month = diff.months
            # months = m + month
            # if rec.invoice_terms == "monthly":
            #     rec.invoice_number = month + m
            # if rec.invoice_terms == "quarterly":
            #     rec.invoice_number = months / 3
            # if rec.invoice_terms == "semi":
            #     rec.invoice_number = months / 6
            # if rec.invoice_terms == "yearly":
            #     rec.invoice_number = diff.years

    def action_confirm(self):
        if self.invoice_number == 0:
            # self.get_invoice_number()
            raise UserError(_('من فضلك اكتب عدد الفواتير'))
        result = super(RentSaleOrder, self).action_confirm()
        if self.is_rental_order:
            self.create_order_invoices()
        return result

    full_invoiced = fields.Boolean(string="Fully Invoiced", compute="_compute_full_invoiced", store=True)
    no_of_invoiced = fields.Integer(string="عدد الفواتير المفوترة", compute="compute_no_invoiced", store=True)
    no_of_not_invoiced = fields.Integer(string="عدد الفواتير الغير مفوترة", compute="compute_no_invoiced", store=True)
    no_of_invoiced_amount = fields.Float(string="المبالغ المفوترة", compute="compute_no_invoiced", store=True)
    no_of_not_invoiced_amount = fields.Float(string="المبالغ الغير مفوترة", compute="compute_no_invoiced", store=True)

    @api.depends('order_contract_invoice.status', 'order_contract_invoice.amount')
    def compute_no_invoiced(self):
        for order in self:
            order.no_of_invoiced = 0
            order.no_of_not_invoiced = 0
            order.no_of_invoiced_amount = 0
            order.no_of_not_invoiced_amount = 0
            order.no_of_invoiced = len(order.order_contract_invoice.filtered(lambda s: s.status == 'invoiced'))
            order.no_of_invoiced_amount = sum(
                order.order_contract_invoice.filtered(lambda s: s.status == 'invoiced').mapped('amount'))
            order.no_of_not_invoiced = len(order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced'))
            order.no_of_not_invoiced_amount = sum(
                order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced').mapped('amount'))

    @api.depends('order_contract_invoice.status')
    def _compute_full_invoiced(self):
        for order in self:
            order.full_invoiced = False
            not_invoiced = order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced')
            if not not_invoiced and len(order.order_contract_invoice) > 0:
                order.full_invoiced = True

    def create_invoices_button(self):
        for i in self:
            if i.order_contract_invoice:

                # separate = False
                # for s in i.order_contract_invoice:
                #     if s.separate:
                #         separate = True
                #         break

                for rec in i.order_contract_invoice:
                    if rec.status == "uninvoiced":
                        invoice_lines = []
                        # if separate:
                        #     if rec.separate:
                        #         invoiceable_lines = i.order_line.filtered(
                        #             lambda s: s.product_id.product_tmpl_id.separate == True)
                        #     else:
                        #         invoiceable_lines = i.order_line.filtered(
                        #             lambda s: s.product_id.product_tmpl_id.separate == False)
                        # else:
                        invoiceable_lines = rec.sale_order_line_ids

                        # if rec.sequence == 1:
                            # seq = 0
                            # for type in INSURANCE_ADMIN_FEES_FIELDS:
                            #     seq += 1
                            #     fees_sum = rec._prepare_invoice_line_insurance_admin_fees_sum(type, seq)
                            #     if fees_sum.get('name', False):
                            #         invoice_lines.append([0, 0, fees_sum])
                        for line in invoiceable_lines:
                            invoice_lines.append([0, 0, rec._prepare_invoice_line(line)])
                            # if rec.sequence == 1:
                            #     seq = 0
                            #     for type in INSURANCE_ADMIN_FEES_FIELDS:
                            #         seq += 1
                            #         if line.mapped(type)[0] > 0:
                            #             invoice_lines.append(
                            #                 [0, 0, rec._prepare_invoice_line_insurance_admin_fees(type, line, seq)])

                        vals = rec._prepare_invoice(invoice_lines)
                        print(vals)
                        self.env['account.move'].create(vals)
                        rec.status = 'invoiced'


class RentSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # product_id = fields.Many2one(
    #     'product.product', string='Product',
    #     domain="[('product_tmpl_id.property_id','=',property_number),('product_tmpl_id.state_id','=','شاغرة')]",
    #     change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
    # product_template_id = fields.Many2one(
    #     'product.template', string='Product Template',
    #     related="product_id.product_tmpl_id", domain=[('sale_ok', '=', True)])

    property_number = fields.Many2one('rent.property', string='العقار')
    property_analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي',
                                                related='property_number.analytic_account')
    analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي',
                                       related='product_id.product_tmpl_id.analytic_account')
    pickup_date = fields.Datetime(string="Pickup", related='order_id.fromdate', store=True)
    return_date = fields.Datetime(string="Return", related='order_id.todate', store=True)
    insurance_value = fields.Float(string='قيمة التأمين')
    contract_admin_fees = fields.Float(string='رسوم ادارية')
    contract_service_fees = fields.Float(string='رسوم الخدمات')
    contract_admin_sub_fees = fields.Float(string='رسوم ادارية خاضعة')
    contract_service_sub_fees = fields.Float(string='رسوم الخدمات خاضعة')
    # Rental Additional Service
    rent_ok = fields.Boolean(related='product_id.product_tmpl_id.rent_ok')
    rent_product_id = fields.Many2one(comodel_name="product.product")
    rental_pricing_id = fields.Many2one(comodel_name="rental.pricing", string="Rental Pricing",
                                        domain="[('product_template_id','=',product_template_id)]")
    service_line_ids = fields.One2many('sale.order.line', 'original_line_id', string='Service Lines')
    original_line_id = fields.Many2one('sale.order.line', string='Original Line')

    def get_hijri_from_gregorian(self, date_gregorian):
        hijri = Gregorian(date_gregorian.year, date_gregorian.month, date_gregorian.day).to_hijri()
        return str(hijri.day) + '-' + str(hijri.month) + '-' + str(hijri.year)

    def get_sale_order_line_multiline_description_sale(self, product):
        description = super(RentSaleOrderLine, self).get_sale_order_line_multiline_description_sale(product)
        if self.pickup_date:
            description += "\n" + (self.get_hijri_from_gregorian(self.pickup_date.date()))

        if self.return_date:
            description += "\n" + 'to  ' + (self.get_hijri_from_gregorian(self.return_date.date()))

        return description

    def action_get_service(self):
        sequence = self.line_sequence
        line_year_number = self.line_year_number
        new_line_ids = []  # List to store the IDs of the newly created lines

        for rec in self.rental_pricing_id.service_ids:
            if rec.type == 'percentage':
                price = self.price_unit * (rec.percentage / 100)
            if rec.type == 'amount':
                price = rec.percentage

            past_lines = self.env['sale.order.line'].browse(self.service_line_ids.ids)
            if len(past_lines) > 0:
                for line in past_lines:
                    line.unlink()

            sequence += 1
            new_line = self.env['sale.order.line'].sudo().create({
                'sequence': sequence,
                'line_sequence': sequence,
                'line_year_number': line_year_number,
                'product_uom_qty': 1,
                'product_id': rec.service_id.product_variant_id.id,
                'name': rec.service_id.product_variant_id.name,
                'order_id': self.order_id.id,
                'analytic_account': self.analytic_account.id,
                'price_unit': price,
                'rent_product_id': self.product_id.id,
            })
            new_line_ids.append(new_line.id)  # Add the new line's ID to the list
        self.write({'service_line_ids': [(6, 0, new_line_ids)]})

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit + line.insurance_value + line.contract_admin_fees + line.contract_service_fees + line.contract_admin_sub_fees + line.contract_service_sub_fees * (
                    1 - (line.discount or 0.0) / 100.0)
            price_tax = line.price_unit + line.contract_admin_sub_fees + line.contract_service_sub_fees * (
                    1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price_tax, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': price,
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    @api.onchange('product_id')
    def check_rental_details(self):
        if self.product_id.product_tmpl_id.rent_ok:
            self.is_rental = True
            for pricing_unit in self.product_id.product_tmpl_id.rental_pricing_ids:
                self.rental_pricing_id = pricing_unit
                break
