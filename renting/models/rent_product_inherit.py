# -*- coding: utf-8 -*-

from odoo import api, models, fields


class RentProduct(models.Model):
    _inherit = 'product.template'

    unit_number = fields.Char(string='رقم الوحدة')
    unit_area = fields.Char(string='مساحة الوحدة')
    unit_floor_number = fields.Char(string='رقم الطابق')
    unit_rooms_number = fields.Char(string='عدد الغرف')
    unit_state = fields.Char(compute='_get_state', string='الحالة', default='شاغرة')

    rent_unit_area = fields.Float(string='المساحة')

    # unit_contain_two_scales = fields.Boolean(string='Contain Two Scales')
    # unit_furniture = fields.Boolean(string='Furniture?')
    furniture_bedroom = fields.Boolean(string='غرفة نوم')
    furniture_bedroom_no = fields.Integer(string=' عدد غرف النوم')
    furniture_bathroom = fields.Boolean(string='حمام')
    furniture_bathroom_no = fields.Integer(string=' عدد الحمام')
    furniture_reception = fields.Boolean(string='ريسيبشن')
    furniture_reception_no = fields.Integer(string=' عدد الريسيبشن')
    furniture_kitchen = fields.Boolean(string='مطبخ')
    furniture_service_room = fields.Boolean(string='غرفة خدم')
    furniture_inventory = fields.Boolean(string='مخزن')
    furniture_inventory_no = fields.Integer(string=' عدد المخازن')
    furniture_setting_room = fields.Boolean(string='غرفة المعيشة')
    furniture_setting_room_no = fields.Integer(string=' عدد غرف المعيشة')
    furniture_central_air_conditioner = fields.Boolean(string='تكييف مركزي')
    furniture_split_air_conditioner = fields.Boolean(string='تكييف سبليت')
    furniture_split_air_conditioner_no = fields.Integer(string=' عدد تكييف سبليت')
    furniture_evaporator_cooler = fields.Boolean(string='مدخنة')
    furniture_evaporator_cooler_no = fields.Integer(string=' عدد المداخن')
    furniture_kitchen_installed = fields.Boolean(string='مطبخ مجهز')
    furniture_locker_installed = fields.Boolean(string='غرفة ملابس')
    furniture_locker_installed_no = fields.Integer(string=' عدد غرف الملابس')

    unit_construction_date = fields.Date(string='تاريخ الانشاء')

    rent_config_unit_overlook_id = fields.Many2one('rent.config.unit.overlooks', string='Unit Overlooking',
                                                   copy=True)  # Related field to menu item "Unit Views"
    rent_config_unit_type_id = fields.Many2one('rent.config.unit.types', string='Unit type',
                                               copy=True)  # Related field to menu item "Unit Types"
    rent_config_unit_purpose_id = fields.Many2one('rent.config.unit.purposes', string='Unit Purpose',
                                                  copy=True)  # Related field to menu item "Unit Purpose"
    rent_config_unit_finish_id = fields.Many2one('rent.config.unit.finishes', string='Unit Finish',
                                                 copy=True)  # Related field to menu item "Unit Finishes"

    property_id = fields.Many2one('rent.property', string='عمارة', copy=True)  # Related field to Properties
    property_address_build = fields.Many2one('rent.property.build', string='المجمع',
                                             related='property_id.property_address_build', store=True, index=True)
    property_address_city = fields.Many2one('rent.property.city', string='المدينة',
                                            related='property_id.property_address_city', store=True)
    country = fields.Many2one('res.country', string='الدولة', related='property_id.country', store=True, index=True)
    operating_unit = fields.Many2many('operating.unit', string='الفرع ')

    entry_number = fields.Char('عدد المداخل')
    entry_overlook = fields.Char('المداخل تطل علي')

    unit_gas = fields.Char(string='رقم عداد الغاز')
    unit_electricity = fields.Char(string='رقم عداد الكهرباء')
    unit_water = fields.Char(string='رقم عداد المياه')

    # unit_maintenance_count = fields.Integer(string='Total Maintenance', compute='_get_count', readonly=True)
    unit_expenses_count = fields.Integer(string='Total Expenses', compute='_unit_expenses_count', readonly=True)
    unit_sales_count = fields.Integer(string='Total Sales', compute='_unit_sales_count', readonly=True)
    unit_price = fields.Float(string='قيمة الوحدة', compute='_get_unit_price')
    unit_price_unit = fields.Char(string='مدة تأجير الوحدة')
    state_id = fields.Char()
    analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي', readonly=True)
    ref_analytic_account = fields.Char(string='رقم اشارة الحساب التحليلي', readonly=True)
    property_analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي للعقار',
                                                related='property_id.analytic_account')
    property_analytic_account_parent = fields.Many2one('account.analytic.group',
                                                       related='property_id.analytic_account.group_id')
    
    # Additional Service
    additional_service_ids = fields.One2many(comodel_name="rental.additional.service", inverse_name="product_id")
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
                elif order[0].order_id.rental_status == 'return':
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                elif order[0].order_id.rental_status == 'returned':
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
                elif order[0].order_id.rental_status == 'cancel':
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
            else:
                rec.state_id = 'شاغرة'
                rec.unit_state = 'شاغرة'

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


class RentalAdditionalService(models.Model):
    _name = 'rental.additional.service'
    _rec_name = 'name'
    name = fields.Char(string="Name",compute='get_concatenation_name' )
    service_id = fields.Many2one(comodel_name="product.template", string="Service", required=True, )
    percentage = fields.Float(string="Percentage",  required=True, )
    product_id = fields.Many2one(comodel_name="product.template")
    def get_concatenation_name(self):
        for rec in self:
            rec.name=rec.service_id.name+"-"+str(rec.percentage)+"%"