# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class /odoo15/custom/addons/ifna-invest/(models.Model):
#     _name = '/odoo15/custom/addons/ifna-invest/./odoo15/custom/addons/ifna-invest/'
#     _description = '/odoo15/custom/addons/ifna-invest/./odoo15/custom/addons/ifna-invest/'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
