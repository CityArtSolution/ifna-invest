# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from lxml import etree


class RentalProcessingLine(models.TransientModel):
    _inherit = 'rental.order.wizard.line'
    _description = 'RentalOrderLine transient representation'

    def _apply(self):
        """Apply the wizard modifications to the SaleOrderLine.

        :return: message to log on the Sales Order.
        :rtype: str
        """
        msg = self._generate_log_message()
        for wizard_line in self:
            order_line = wizard_line.order_line_id
            if wizard_line.status == 'pickup' and wizard_line.qty_delivered > 0:
                order_line.product_id.state_id = 'مؤجرة'
                order_line.product_id.unit_state = 'مؤجرة'
                order_line.product_id.product_tmpl_id.state_id = 'مؤجرة'
                order_line.product_id.product_tmpl_id.unit_state = 'مؤجرة'

                order_line.update({
                    'product_uom_qty': max(order_line.product_uom_qty,
                                           order_line.qty_delivered + wizard_line.qty_delivered),
                    'qty_delivered': order_line.qty_delivered + wizard_line.qty_delivered
                })
                if order_line.pickup_date > fields.Datetime.now():
                    order_line.pickup_date = fields.Datetime.now()

            elif wizard_line.status == 'return' and wizard_line.qty_returned > 0:
                order_line.product_id.state_id = 'شاغرة'
                order_line.product_id.unit_state = 'شاغرة'
                order_line.product_id.product_tmpl_id.state_id = 'شاغرة'
                order_line.product_id.product_tmpl_id.unit_state = 'شاغرة'
                if wizard_line.is_late:
                    # Delays facturation
                    order_line._generate_delay_line(wizard_line.qty_returned)

                order_line.update({
                    'qty_returned': order_line.qty_returned + wizard_line.qty_returned
                })
        return msg


class RentProductProduct(models.Model):
    _inherit = 'product.product'

    # unit_number = fields.Char(string='رقم الوحدة', copy=True)
    # unit_area = fields.Char(string='مساحة الوحدة', copy=True)
    # unit_floor_number = fields.Char(string='رقم الطابق', copy=True)
    # unit_rooms_number = fields.Char(string='عدد الغرف', copy=True)
    # unit_state = fields.Char(string='الحالة', default='شاغرة', copy=True)

    # rent_unit_area = fields.Float(string='المساحة', copy=True)

    # unit_contain_two_scales = fields.Boolean(string='Contain Two Scales')
    # unit_furniture = fields.Boolean(string='Furniture?')
    # furniture_bedroom = fields.Boolean(string='غرفة نوم', copy=True)
    # furniture_bedroom_no = fields.Integer(string=' عدد غرف النوم', copy=True)
    # furniture_bathroom = fields.Boolean(string='حمام', copy=True)
    # furniture_bathroom_no = fields.Integer(string=' عدد الحمام', copy=True)
    # furniture_reception = fields.Boolean(string='ريسيبشن', copy=True)
    # furniture_reception_no = fields.Integer(string=' عدد الريسيبشن', copy=True)
    # furniture_kitchen = fields.Boolean(string='مطبخ', copy=True)
    # furniture_service_room = fields.Boolean(string='غرفة خدم', copy=True)
    # furniture_inventory = fields.Boolean(string='مخزن', copy=True)
    # furniture_inventory_no = fields.Integer(string=' عدد المخازن', copy=True)
    # furniture_setting_room = fields.Boolean(string='غرفة المعيشة', copy=True)
    # furniture_setting_room_no = fields.Integer(string=' عدد غرف المعيشة', copy=True)
    # furniture_central_air_conditioner = fields.Boolean(string='تكييف مركزي', copy=True)
    # furniture_split_air_conditioner = fields.Boolean(string='تكييف سبليت', copy=True)
    # furniture_split_air_conditioner_no = fields.Integer(string=' عدد تكييف سبليت', copy=True)
    # furniture_evaporator_cooler = fields.Boolean(string='مدخنة', copy=True)
    # furniture_evaporator_cooler_no = fields.Integer(string=' عدد المداخن', copy=True)
    # furniture_kitchen_installed = fields.Boolean(string='مطبخ مجهز', copy=True)
    # furniture_locker_installed = fields.Boolean(string='غرفة ملابس', copy=True)
    # furniture_locker_installed_no = fields.Integer(string=' عدد غرف الملابس', copy=True)

    # unit_construction_date = fields.Date(string='تاريخ الانشاء', copy=True)

    # rent_config_unit_overlook_id = fields.Many2one('rent.config.unit.overlooks', string='Unit Overlooking',
    #                                                copy=True)  # Related field to menu item "Unit Views"
    # rent_config_unit_type_id = fields.Many2one('rent.config.unit.types', string='Unit type - Style',
    #                                            copy=True)  # Related field to menu item "Unit Types"
    # rent_config_unit_purpose_id = fields.Many2one('rent.config.unit.purposes', string='Unit Purpose',
    #                                               copy=True)  # Related field to menu item "Unit Purpose"
    # rent_config_unit_finish_id = fields.Many2one('rent.config.unit.finishes', string='Unit Finish',
    #                                              copy=True)  # Related field to menu item "Unit Finishes"

    # property_id = fields.Many2one('rent.property', string='عمارة', copy=True)  # Related field to Properties

    # operating_unit = fields.Many2many('operating.unit', string='الفرع ', copy=True)

    # entry_number = fields.Char('عدد المداخل', copy=True)
    # entry_overlook = fields.Char('المداخل تطل علي', copy=True)

    # unit_gas = fields.Char(string='رقم عداد الغاز', copy=True)
    # unit_electricity = fields.Char(string='رقم عداد الكهرباء', copy=True)
    # unit_water = fields.Char(string='رقم عداد المياه', copy=True)

    # unit_maintenance_count = fields.Integer(string='Total Maintenance', compute='_get_count', readonly=True)
    unit_expenses_count = fields.Integer(string='Total Expenses', compute='_unit_expenses_count', readonly=True)
    unit_price_unit = fields.Char(string='مدة تأجير الوحدة', copy=True)
    state_id = fields.Char(default="_get_state", store=True)
    analytic_account = fields.Many2one('account.analytic.account', copy=True, string='الحساب التحليلي', readonly=True)
    ref_analytic_account = fields.Char(string='رقم اشارة الحساب التحليلي', readonly=True)

    # property_analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي للعقار',
    #                                             related='property_id.analytic_account')
    # property_id = fields.Many2one('rent.property', string='عمارة', copy=True)  # Related field to Properties

    def _get_state_rent_of_unit(self):
        for rec in self:
            print('11111')
            rec.state_id = 'شاغرة'
            rec.unit_state = 'شاغرة'
            order = self.env['sale.order.line'].search(
                [('product_id', '=', self._origin.id), ('property_number', '=', self.property_id.id)])
            # order = rec.env['sale.order.line'].sudo().search(
            #     [('product_id', '=', rec.id), ('property_number', '=', rec.property_id.id)])
            if order:
                print('order', order, order[0].order_id.rental_status)
                if order[0].order_id.rental_status == 'return':
                    print('yes return')
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                elif order[0].order_id.rental_status == 'returned':
                    print('yes returned')
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
                elif order[0].order_id.rental_status == 'cancel':
                    print('yes cancel')
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
            else:
                print('nooo')
                rec.state_id = 'شاغرة'
                rec.unit_state = 'شاغرة'

    @api.model
    def _get_state(self):
        for rec in self:
            rec.unit_state = 'شاغرة'
            rec.state_id = 'شاغرة'
            order = rec.env['sale.order.line'].sudo().search(
                [('product_id', '=', rec.id), ('property_number', '=', rec.property_id.property_name)])
            if order:
                if order[0].order_id.rental_status == 'pickup':
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                    return 'مؤجرة'
                elif order[0].order_id.rental_status == 'return':
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                    return 'مؤجرة'
                elif order[0].order_id.rental_status == 'returned':
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
                    return 'شاغرة'
                elif order[0].order_id.rental_status == 'cancel':
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
                    return 'شاغرة'
            else:
                rec.state_id = 'شاغرة'
                rec.unit_state = 'شاغرة'
                return 'شاغرة'


class RentProduct(models.Model):
    _inherit = 'product.template'

    separate = fields.Boolean(string="Separate Invoice")
    fees_type = fields.Selection([('admin', 'Admin Fee'), ('security', 'Security Deposit'), ('other', 'Other')],
                                 string='Fees Type')

    unit_number = fields.Char(string='رقم الوحدة', copy=True)
    unit_area = fields.Char(string='مساحة الوحدة', copy=True)
    unit_floor_number = fields.Char(string='رقم الطابق', copy=True)
    unit_rooms_number = fields.Char(string='عدد الغرف', copy=True)
    unit_state = fields.Char(string='الحالة', default='شاغرة', copy=True)

    # unit_contain_two_scales = fields.Boolean(string='Contain Two Scales')
    # unit_furniture = fields.Boolean(string='Furniture?')
    furniture_bedroom = fields.Boolean(string='غرفة نوم', copy=True)
    furniture_bedroom_no = fields.Integer(string=' عدد غرف النوم', copy=True)
    furniture_bathroom = fields.Boolean(string='حمام', copy=True)
    furniture_bathroom_no = fields.Integer(string=' عدد الحمام', copy=True)
    furniture_reception = fields.Boolean(string='ريسيبشن', copy=True)
    furniture_reception_no = fields.Integer(string=' عدد الريسيبشن', copy=True)
    furniture_kitchen = fields.Boolean(string='مطبخ', copy=True)
    furniture_service_room = fields.Boolean(string='غرفة خدم', copy=True)
    furniture_inventory = fields.Boolean(string='مخزن', copy=True)
    furniture_inventory_no = fields.Integer(string=' عدد المخازن', copy=True)
    furniture_setting_room = fields.Boolean(string='غرفة المعيشة', copy=True)
    furniture_setting_room_no = fields.Integer(string=' عدد غرف المعيشة', copy=True)
    furniture_central_air_conditioner = fields.Boolean(string='تكييف مركزي', copy=True)
    furniture_split_air_conditioner = fields.Boolean(string='تكييف سبليت', copy=True)
    furniture_split_air_conditioner_no = fields.Integer(string=' عدد تكييف سبليت', copy=True)
    furniture_evaporator_cooler = fields.Boolean(string='مدخنة', copy=True)
    furniture_evaporator_cooler_no = fields.Integer(string=' عدد المداخن', copy=True)
    furniture_kitchen_installed = fields.Boolean(string='مطبخ مجهز', copy=True)
    furniture_locker_installed = fields.Boolean(string='غرفة ملابس', copy=True)
    furniture_locker_installed_no = fields.Integer(string=' عدد غرف الملابس', copy=True)

    unit_construction_date = fields.Date(string='تاريخ الانشاء', copy=True)

    rent_config_unit_overlook_id = fields.Many2one('rent.config.unit.overlooks', string='Unit Overlooking',
                                                   copy=True)  # Related field to menu item "Unit Views"
    rent_config_unit_type_id = fields.Many2one('rent.config.unit.types', string='Unit type - Style',
                                               copy=True)  # Related field to menu item "Unit Types"
    rent_config_unit_purpose_id = fields.Many2one('rent.config.unit.purposes', string='Unit Purpose',
                                                  copy=True)  # Related field to menu item "Unit Purpose"
    rent_config_unit_finish_id = fields.Many2one('rent.config.unit.finishes', string='Unit Finish',
                                                 copy=True)  # Related field to menu item "Unit Finishes"

    property_id = fields.Many2one('rent.property', string='عمارة', copy=True)  # Related field to Properties
    property_address_build = fields.Many2one('rent.property.build', copy=True, string='المجمع',
                                             related='property_id.property_address_build', store=True, index=True)
    property_address_city = fields.Many2one('rent.property.city', string='المدينة', copy=True,
                                            related='property_id.property_address_city', store=True)
    country = fields.Many2one('res.country', string='الدولة', related='property_id.country', store=True, index=True,
                              copy=True)
    operating_unit = fields.Many2many('operating.unit', string='الفرع ', copy=True)

    entry_number = fields.Char('عدد المداخل', copy=True)
    entry_overlook = fields.Char('المداخل تطل علي', copy=True)

    unit_gas = fields.Char(string='رقم عداد الغاز', copy=True)
    unit_electricity = fields.Char(string='رقم عداد الكهرباء', copy=True)
    # unit_electricity_cut = fields.Char(string='رقم عداد الكهرباء', copy=True)
    unit_water = fields.Char(string='رقم عداد المياه', copy=True)

    # unit_maintenance_count = fields.Integer(string='Total Maintenance', compute='_get_count', readonly=True)
    unit_expenses_count = fields.Integer(string='Total Expenses', compute='_unit_expenses_count', readonly=True)
    unit_sales_count = fields.Integer(string='Total Sales', compute='_unit_sales_count', readonly=True)
    unit_price = fields.Float(string='قيمة الوحدة', compute='_get_unit_price')
    unit_price_unit = fields.Char(string='مدة تأجير الوحدة', copy=True)
    state_id = fields.Char(default="_get_state", store=True)
    analytic_account = fields.Many2one('account.analytic.account', copy=True, string='الحساب التحليلي', readonly=True)
    ref_analytic_account = fields.Char(string='رقم اشارة الحساب التحليلي', readonly=True)
    property_analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي للعقار',
                                                related='property_id.analytic_account')
    property_analytic_account_parent = fields.Many2one('account.analytic.group',
                                                       related='property_id.analytic_account.group_id')
    # Additional Service
    additional_service_ids = fields.One2many(comodel_name="rental.additional.service", inverse_name="product_id")

    @api.model
    def _get_state(self):
        for rec in self:
            rec.unit_state = 'شاغرة'
            rec.state_id = 'شاغرة'
            order = rec.env['sale.order.line'].sudo().search(
                [('product_id', '=', rec.id), ('property_number', '=', rec.property_id.property_name)])
            if order:
                if order[0].order_id.rental_status == 'pickup':
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                    return 'مؤجرة'
                elif order[0].order_id.rental_status == 'return':
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                    return 'مؤجرة'
                elif order[0].order_id.rental_status == 'returned':
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
                    return 'شاغرة'
                elif order[0].order_id.rental_status == 'cancel':
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
                    return 'شاغرة'
            else:
                rec.state_id = 'شاغرة'
                rec.unit_state = 'شاغرة'
                return 'شاغرة'

    def _get_state_rent_of_unit(self):
        for rec in self:
            print('11111')
            rec.state_id = 'شاغرة'
            rec.unit_state = 'شاغرة'
            order = self.env['sale.order.line'].search(
                [('product_id', '=', self._origin.id), ('property_number', '=', self.property_id.id)])
            # order = rec.env['sale.order.line'].sudo().search(
            #     [('product_id', '=', rec.id), ('property_number', '=', rec.property_id.id)])
            if order:
                print('order', order, order[0].order_id.rental_status)
                if order[0].order_id.rental_status == 'return':
                    print('yes return')
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                elif order[0].order_id.rental_status == 'returned':
                    print('yes returned')
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
                elif order[0].order_id.rental_status == 'cancel':
                    print('yes cancel')
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
            else:
                print('nooo')
                rec.state_id = 'شاغرة'
                rec.unit_state = 'شاغرة'

    def write(self, values):
        if 'name' in values:
            name = values.get('name')
            if self.analytic_account:
                self.analytic_account.name = name
        if 'unit_number' in values:
            unit_number = values.get('unit_number')
            if self.analytic_account:
                self.analytic_account.code = str(self.property_id.ref_analytic_account) + '-' + str(unit_number)
        result = super(RentProduct, self).write(values)
        return result

    @api.model_create_multi
    def create(self, vals_list):
        res = super(RentProduct, self).create(vals_list)
        if res.rent_ok:
            res.ref_analytic_account = str(res.property_id.ref_analytic_account) + '-' + str(res.unit_number)
            analytic_account = self.env['account.analytic.account'].sudo().create(
                {'name': res.name, 'group_id': res.property_analytic_account_parent.id,
                 'code': res.ref_analytic_account})
            res.analytic_account = analytic_account
        return res

    def _get_unit_price(self):
        for rec in self:
            prices = []
            units = []
            for price in rec.rental_pricing_ids:
                prices.append(price.price)
                units.append(price.unit)
            if len(prices) > 0:
                rec.unit_price = prices[0]
            if len(units) > 0:
                rec.unit_price_unit = units[0]
            else:
                rec.unit_price = 0
                rec.unit_price_unit = ''

    # @api.depends('state_id')
    # def _get_state(self):
    #     for rec in self:
    #         print("/////////", rec.state_id)
    #         rec.unit_state = 'شاغرة'
    #         rec.state_id = 'شاغرة'
    #         order = rec.env['sale.order.line'].sudo().search(
    #             [('product_id', '=', rec.id), ('property_number', '=', rec.property_id.property_name)])
    #         if order:
    #             if order[0].order_id.rental_status == 'pickup':
    #                 rec.state_id = 'مؤجرة'
    #                 rec.unit_state = 'مؤجرة'
    #             elif order[0].order_id.rental_status == 'return':
    #                 rec.state_id = 'مؤجرة'
    #                 rec.unit_state = 'مؤجرة'
    #             elif order[0].order_id.rental_status == 'returned':
    #                 rec.state_id = 'شاغرة'
    #                 rec.unit_state = 'شاغرة'
    #             elif order[0].order_id.rental_status == 'cancel':
    #                 rec.state_id = 'شاغرة'
    #                 rec.unit_state = 'شاغرة'
    #         else:
    #             rec.state_id = 'شاغرة'
    #             rec.unit_state = 'شاغرة'

    # def _get_count(self):
    #     self.unit_maintenance_count = self.env['account.move'].search_count(
    #         [('unit_number', '=', self.id), ('property_name', '=', self.property_id.property_name),
    #          ('move_type', '=', 'in_invoice')])

    # For Unit Maintenance Button in rent_product_inherit_form in "vw_rent_product_inherit.xml"
    def get_unit_maintenance(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'صيانات',
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': {'default_move_type': 'in_invoice', 'default_journal_id': 2,
                        'default_property_name': self.property_id.id,
                        'default_unit_number': self.id, 'default_analytic_account': self.analytic_account.id},
        }

    def _unit_sales_count(self):
        self.unit_sales_count = self.env['sale.order.line'].search_count(
            [('product_id', '=', self.id), ('property_number', '=', self.property_id.property_name)])

    # For Unit Maintenance Button in rent_product_inherit_form in "vw_rent_product_inherit.xml"
    def unit_sales(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'ايجارات',
            'view_mode': 'form',
            'view_id': self.env.ref('sale_renting.rental_order_primary_form_view').id,
            'res_model': 'sale.order',
            'context': {'default_is_rental_order': True, 'default_property_name': self.property_id.id,
                        'default_unit_number': self.id, 'default_analytic_account_id': self.analytic_account.id},
        }

    def display_product_form(self):
        """Display details of product."""
        self.ensure_one()
        return {
            'name': _('Product'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.template',
            'type': 'ir.actions.act_window',
            'res_id': self.id
        }


class RentalAdditionalService(models.Model):
    _name = 'rental.additional.service'
    _rec_name = 'name'

    name = fields.Char(string="Name", compute='get_concatenation_name')
    service_id = fields.Many2one(comodel_name="product.template", string="Service", required=True, )
    type = fields.Selection(
        [('amount', 'Amount'), ('percentage', 'Percentage')],
        string='Type',
        default='amount')
    fixed = fields.Float()
    percentage = fields.Float()
    product_id = fields.Many2one(comodel_name="product.template")
    separate = fields.Boolean(string="Separate Invoice")
    fees_type = fields.Selection([('admin', 'Admin Fee'), ('security', 'Security Deposit'), ('other', 'Other')],
                                 string='Fees Type')

    @api.onchange('separate')
    def change_separate(self):
        for rec in self:
            if rec.separate:
                rec.service_id.separate = True
            else:
                rec.service_id.separate = False

    @api.model
    def create(self, vals):
        result = super(RentalAdditionalService, self).create(vals)
        if result.separate:
            result.service_id.separate = True
        if result.fees_type:
            result.service_id.fees_type = result.fees_type
        return result

    @api.onchange('fees_type')
    def change_fees_type(self):
        for rec in self:
            if rec.fees_type:
                rec.service_id.fees_type = rec.fees_type

    def get_concatenation_name(self):
        for rec in self:
            rec.name = rec.service_id.name
