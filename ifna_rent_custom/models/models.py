from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class RentCustom(models.Model):
    _inherit = 'rent.property'

    maintain_company = fields.Many2one(comodel_name="res.partner",string='شركة الصيانة')
    security_company = fields.Many2one(comodel_name="res.partner",string='شركة الأمن')
    cleaning_company = fields.Many2one(comodel_name="res.partner",string='شركة النظافة')

    municipal_side_id = fields.Many2one(comodel_name="res.partner", string=" جهة البلدية ", required=False, )
    civil_defense_authority_id = fields.Many2one(comodel_name="res.partner", string="  جهة الدفاع المدني ", required=False, )
    side_tourism_id = fields.Many2one(comodel_name="res.partner", string="  جهة وزارة السياحة ", required=False, )
    side_housing_id = fields.Many2one(comodel_name="res.partner", string="  جهة وزارة الاسكان  ", required=False, )
    trade_permit_number_id = fields.Many2one(comodel_name="res.partner", string="  جهة السجل التجاري   ", required=False, )


class RentPropertySecurityCustom(models.Model):
    _inherit = 'security.rent.property'

    security_name = fields.Many2one(comodel_name="res.partner", string="اسم  حارس العقار", )
