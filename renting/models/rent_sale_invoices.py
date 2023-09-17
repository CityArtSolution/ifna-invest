# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

INSURANCE_ADMIN_FEES_PRODUCTS = ['insurance_value', 'contract_admin_fees', 'contract_service_fees',
                                 'contract_admin_sub_fees', 'contract_service_sub_fees']
INSURANCE_ADMIN_FEES_FIELDS = ['insurance_value', 'contract_admin_fees', 'contract_service_fees',
                               'contract_admin_sub_fees', 'contract_service_sub_fees']

from datetime import timedelta
from hijri_converter import Hijri, Gregorian

class RentSaleInvoices(models.Model):
    _name = 'rent.sale.invoices'

    sale_order_id = fields.Many2one('sale.order', copy=True, string='العقود', ondelete='cascade')
    sale_order_line_ids = fields.Many2many('sale.order.line', copy=True, ondelete='cascade')
    name = fields.Char(string='Label')
    sequence = fields.Integer(string='Sequence')
    amount = fields.Float(string='Amount')
    invoice_date = fields.Date(string='Invoice Date')
    status = fields.Selection([('uninvoiced', 'Un Invoiced'), ('invoiced', 'Invoiced')], string='Status',
                              default="uninvoiced")
    fromdate = fields.Datetime(string='From Date', default=fields.Date.context_today, copy=False, required=True)
    todate = fields.Datetime(string='To Date', default=fields.Date.context_today, copy=False, required=True)
    operating_unit = fields.Many2one('operating.unit', string='Operating Unit')
    services = fields.Many2many('product.product', string='Services')
    separate = fields.Boolean(string="Separate Invoice")

    def _get_hijri_date(self,date):
        return Gregorian(date.year, date.month,
                                                  date.day).to_hijri()
    def _prepare_invoice_line(self, line):
        self.ensure_one()
        terms = 0
        if line.order_id.invoice_terms == "monthly":
            terms = 12
        if line.order_id.invoice_terms == "quarterly":
            terms = 4
        if line.order_id.invoice_terms == "semi":
            terms = 2
        if line.order_id.invoice_terms == "yearly":
            terms = 1
        # if self.separate:
        #     price = line.price_unit
        # else:
        #     price = line.price_unit / self.sale_order_id.invoice_number
        res = {
            'display_type': line.display_type,
            'sequence': line.sequence,
            'name': line.name+'\n'+str(self._get_hijri_date(self.fromdate.date()) if self.fromdate else '')+'\n'+'to:  '+str(self._get_hijri_date(self.todate.date())-timedelta(days=1) if self.todate else '')+'\n',
            'product_id': line.product_id.id,
            'product_uom_id': line.product_uom.id,
            'quantity': 1,
            'discount': line.discount,
            'price_unit': line.price_unit/terms,
            'tax_ids': [(6, 0, line.tax_id.ids)],
            'analytic_account_id': line.product_id.product_tmpl_id.analytic_account.id,
            'sale_line_ids': [(4, line.id)],
            'exclude_from_invoice_tab': False,
        }
        # 'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
        # if self.sequence == 1:
        #     res.update({
        #         # 'property_price_unit': line.price_unit / self.sale_order_id.invoice_number,
        #         # 'price_unit': (line.price_unit / self.sale_order_id.invoice_number) + line.contract_admin_sub_fees + line.contract_service_sub_fees,
        #         'price_unit': (line.price_unit / self.sale_order_id.invoice_number),
        #         # 'insurance_value': line.insurance_value,
        #         # 'contract_admin_fees': line.contract_admin_fees,
        #         # 'contract_service_fees': line.contract_service_fees,
        #         # 'contract_admin_sub_fees': line.contract_admin_sub_fees,
        #         # 'contract_service_sub_fees': line.contract_service_sub_fees
        #     })
        return res

    def _prepare_invoice_line_insurance_admin_fees_sum(self, type, seq):
        self.ensure_one()
        res = {}
        type_name = 'renting.' + type
        type_config_parameter = self.env['ir.config_parameter'].sudo().get_param(type_name)
        type_product_template = self.env['product.template'].search([('id', '=', int(type_config_parameter))])
        if not type_product_template:
            raise UserError(_('Please define Insurance and admin fees products in renting setting.'))
        fees_amount = 0
        fees_amount = sum(self.sale_order_id.order_line.mapped(type))
        if fees_amount > 0:
            res = {
                'display_type': 'line_note',
                'sequence': seq + 1000,
                'name': 'إجمالي قيمة ' + type_product_template.name + ': ' + str(fees_amount),
                'exclude_from_invoice_tab': False,
            }
        else:
            res = {
                'name': False,
            }
        return res

    def _prepare_invoice_line_insurance_admin_fees(self, type, line, seq):
        self.ensure_one()
        type_name = 'renting.' + type
        type_config_parameter = self.env['ir.config_parameter'].sudo().get_param(type_name)
        type_product_template = self.env['product.template'].search([('id', '=', int(type_config_parameter))])
        if not type_product_template:
            raise UserError(_('Please define Insurance and admin fees products in renting setting.'))
        fees_amount = line.mapped(type)[0]
        res = {
            'sequence': seq + 1000,
            'name': type_product_template.name,
            'product_id': type_product_template.id,
            'product_uom_id': 1,
            'quantity': 1,
            'price_unit': fees_amount,
            'analytic_account_id': line.product_id.analytic_account.id,
            'tax_ids': [(6, 0, self.sale_order_id.order_line.tax_id.ids)] if type in ['contract_admin_sub_fees',
                                                                                      'contract_service_sub_fees'] else False,
            'exclude_from_invoice_tab': False,
            'rent_fees': True,
            # 'sale_line_ids': [(4, line.id)],
        }
        return res

    def _prepare_invoice(self, invoice_lines):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (
                self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.sale_order_id.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.sale_order_id.note,
            'currency_id': self.sale_order_id.pricelist_id.currency_id.id,
            'campaign_id': self.sale_order_id.campaign_id.id,
            'medium_id': self.sale_order_id.medium_id.id,
            'source_id': self.sale_order_id.source_id.id,
            'user_id': self.sale_order_id.user_id.id,
            'invoice_user_id': self.sale_order_id.user_id.id,
            'team_id': self.sale_order_id.team_id.id,
            'partner_id': self.sale_order_id.partner_invoice_id.id,
            'partner_shipping_id': self.sale_order_id.partner_shipping_id.id,
            'fiscal_position_id': (
                    self.sale_order_id.fiscal_position_id or self.sale_order_id.fiscal_position_id.get_fiscal_position(
                self.sale_order_id.partner_invoice_id.id)).id,
            'partner_bank_id': self.sale_order_id.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.sale_order_id.name,
            'invoice_payment_term_id': self.sale_order_id.payment_term_id.id,
            'payment_reference': self.sale_order_id.reference,
            'transaction_ids': [(6, 0, self.sale_order_id.transaction_ids.ids)],
            "invoice_line_ids": invoice_lines,
            'company_id': self.sale_order_id.company_id.id,
            'operating_unit_id': self.operating_unit.id,
            'invoice_date': self.invoice_date,
            'obj_sale_order': self.sale_order_id.id,
            'fromdate': self.fromdate,
            'todate': self.todate,
        }
        return invoice_vals

    def create_invoices(self):
        invoice_lines = []
        # separate = False
        # for s in self.sale_order_id.order_line:
        #     if s.product_id.product_tmpl_id.separate:
        #         separate = True
        #         break
        # if separate:
        #     if self.separate:
        #         invoiceable_lines = self.sale_order_id.order_line.filtered(
        #             lambda s: s.product_id.product_tmpl_id.separate == True)
        #     else:
        #         invoiceable_lines = self.sale_order_id.order_line.filtered(
        #             lambda s: s.product_id.product_tmpl_id.separate == False)
        # else:
        #     invoiceable_lines = self.sale_order_id.order_line

        # if self.sequence == 1:
        #     seq = 0
        #     for type in INSURANCE_ADMIN_FEES_FIELDS:
        #         seq += 1
        #         fees_sum = self._prepare_invoice_line_insurance_admin_fees_sum(type, seq)
        #         if fees_sum.get('name', False):
        #             invoice_lines.append([0, 0, fees_sum])
        invoiceable_lines = self.sale_order_line_ids
        for line in invoiceable_lines:
            invoice_lines.append([0, 0, self._prepare_invoice_line(line)])
            if self.sequence == 1:
                seq = 0
                for type in INSURANCE_ADMIN_FEES_FIELDS:
                    seq += 1
                    if line.mapped(type)[0] > 0:
                        invoice_lines.append([0, 0, self._prepare_invoice_line_insurance_admin_fees(type, line, seq)])
        vals = self._prepare_invoice(invoice_lines)
        invoice = self.env['account.move'].create(vals)
        self.status = 'invoiced'
        return invoice


class RentSaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    insurance_value = fields.Many2one('product.template', string='التأمين', config_parameter="renting.insurance_value")
    contract_admin_fees = fields.Many2one('product.template', string='رسوم ادارية',
                                          config_parameter="renting.contract_admin_fees")
    contract_service_fees = fields.Many2one('product.template', string='رسوم الخدمات',
                                            config_parameter="renting.contract_service_fees")
    contract_admin_sub_fees = fields.Many2one('product.template', string='رسوم ادارية خاضعة',
                                              config_parameter="renting.contract_admin_sub_fees")
    contract_service_sub_fees = fields.Many2one('product.template', string='رسوم الخدمات خاضعة',
                                                config_parameter="renting.contract_service_sub_fees")


class RentSalestats(models.Model):
    _name = 'rent.sale.state'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    sale_order = fields.Many2one('sale.order', string='Sale Order')
    sale_order_line_id = fields.Many2one('sale.order.line', string='الوحدة', domain="[('order_id', '=', sale_order)]")
    # product_id = fields.Many2one('product.template', string='الوحدة')
    sequence = fields.Integer(string='Sequence')
    h_pickup_date = fields.Char(string='تاريخ محضر الإستلام الهجري')
    pickup_date = fields.Date(string='تاريخ محضر الإستلام')

    h_return_date = fields.Char(string='تاريخ محضر التسليم الهجري')
    return_date = fields.Date(string='تاريخ محضر التسليم')

    wall_good = fields.Boolean('جيد')
    wall_bad = fields.Boolean('سئ')
    wall_none = fields.Boolean('لا يوجد')
    wall_comment = fields.Char('الملاحظات')
    rwall_good = fields.Boolean('جيد')
    rwall_bad = fields.Boolean('سئ')
    rwall_none = fields.Boolean('لا يوجد')
    rwall_comment = fields.Char('الملاحظات')

    floor_good = fields.Boolean('جيد')
    floor_bad = fields.Boolean('سئ')
    floor_none = fields.Boolean('لا يوجد')
    floor_comment = fields.Char('الملاحظات')
    rfloor_good = fields.Boolean('جيد')
    rfloor_bad = fields.Boolean('سئ')
    rfloor_none = fields.Boolean('لا يوجد')
    rfloor_comment = fields.Char('الملاحظات')

    bath_good = fields.Boolean('جيد')
    bath_bad = fields.Boolean('سئ')
    bath_none = fields.Boolean('لا يوجد')
    bath_comment = fields.Char('الملاحظات')
    rbath_good = fields.Boolean('جيد')
    rbath_bad = fields.Boolean('سئ')
    rbath_none = fields.Boolean('لا يوجد')
    rbath_comment = fields.Char('الملاحظات')

    elec_good = fields.Boolean('جيد')
    elec_bad = fields.Boolean('سئ')
    elec_none = fields.Boolean('لا يوجد')
    elec_comment = fields.Char('الملاحظات')
    relec_good = fields.Boolean('جيد')
    relec_bad = fields.Boolean('سئ')
    relec_none = fields.Boolean('لا يوجد')
    relec_comment = fields.Char('الملاحظات')

    water_good = fields.Boolean('جيد')
    water_bad = fields.Boolean('سئ')
    water_none = fields.Boolean('لا يوجد')
    water_comment = fields.Char('الملاحظات')
    rwater_good = fields.Boolean('جيد')
    rwater_bad = fields.Boolean('سئ')
    rwater_none = fields.Boolean('لا يوجد')
    rwater_comment = fields.Char('الملاحظات')

    wate_good = fields.Boolean('جيد')
    wate_bad = fields.Boolean('سئ')
    wate_none = fields.Boolean('لا يوجد')
    wate_comment = fields.Char('الملاحظات')
    rwate_good = fields.Boolean('جيد')
    rwate_bad = fields.Boolean('سئ')
    rwate_none = fields.Boolean('لا يوجد')
    rwate_comment = fields.Char('الملاحظات')

    door_good = fields.Boolean('جيد')
    door_bad = fields.Boolean('سئ')
    door_none = fields.Boolean('لا يوجد')
    door_comment = fields.Char('الملاحظات')
    rdoor_good = fields.Boolean('جيد')
    rdoor_bad = fields.Boolean('سئ')
    rdoor_none = fields.Boolean('لا يوجد')
    rdoor_comment = fields.Char('الملاحظات')

    window_good = fields.Boolean('جيد')
    window_bad = fields.Boolean('سئ')
    window_none = fields.Boolean('لا يوجد')
    window_comment = fields.Char('الملاحظات')
    rwindow_good = fields.Boolean('جيد')
    rwindow_bad = fields.Boolean('سئ')
    rwindow_none = fields.Boolean('لا يوجد')
    rwindow_comment = fields.Char('الملاحظات')

    ac_good = fields.Boolean('جيد')
    ac_bad = fields.Boolean('سئ')
    ac_none = fields.Boolean('لا يوجد')
    ac_comment = fields.Char('الملاحظات')
    rac_good = fields.Boolean('جيد')
    rac_bad = fields.Boolean('سئ')
    rac_none = fields.Boolean('لا يوجد')
    rac_comment = fields.Char('الملاحظات')

    ii_good = fields.Boolean('جيد')
    ii_bad = fields.Boolean('سئ')
    ii_none = fields.Boolean('لا يوجد')
    ii_comment = fields.Char('الملاحظات')
    rii_good = fields.Boolean('جيد')
    rii_bad = fields.Boolean('سئ')
    rii_none = fields.Boolean('لا يوجد')
    rii_comment = fields.Char('الملاحظات')

    geps_good = fields.Boolean('جيد')
    geps_bad = fields.Boolean('سئ')
    geps_none = fields.Boolean('لا يوجد')
    geps_comment = fields.Char('الملاحظات')
    rgeps_good = fields.Boolean('جيد')
    rgeps_bad = fields.Boolean('سئ')
    rgeps_none = fields.Boolean('لا يوجد')
    rgeps_comment = fields.Char('الملاحظات')

    keys_good = fields.Boolean('جيد')
    keys_bad = fields.Boolean('سئ')
    keys_none = fields.Boolean('لا يوجد')
    keys_comment = fields.Char('الملاحظات')
    rkeys_good = fields.Boolean('جيد')
    rkeys_bad = fields.Boolean('سئ')
    rkeys_none = fields.Boolean('لا يوجد')
    rkeys_comment = fields.Char('الملاحظات')

    other_good = fields.Boolean('جيد')
    other_bad = fields.Boolean('سئ')
    other_none = fields.Boolean('لا يوجد')
    other_comment = fields.Char('الملاحظات')
    rother_good = fields.Boolean('جيد')
    rother_bad = fields.Boolean('سئ')
    rother_none = fields.Boolean('لا يوجد')
    rother_comment = fields.Char('الملاحظات')

    il_good = fields.Boolean('تم')
    il_bad = fields.Boolean('لم يتم')
    il_none = fields.Boolean('لا يوجد')
    il_comment = fields.Char('الملاحظات')
    ril_good = fields.Boolean('تم')
    ril_bad = fields.Boolean('لم يتم')
    ril_none = fields.Boolean('لا يوجد')
    ril_comment = fields.Char('الملاحظات')

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
    recent_electricity = fields.Char('قراءة عداد الكهرباء الحالية')
    recent_water = fields.Char('قراءة عداد المياه الحالية')
    rrecent_electricity = fields.Char('قراءة عداد الكهرباء الحالية')
    rrecent_water = fields.Char('قراءة عداد المياه الحالية')
