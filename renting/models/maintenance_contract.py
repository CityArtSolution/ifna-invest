# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceContract(models.Model):
    _name = 'maintenance.contract'
    _description = 'Maintenance Contract'

    vendor_id = fields.Many2one('res.partner', string='شركة الصيانة')
    attachment_id = fields.Binary(string='عقد الصيانة', attachment=True)
    maintenance_type_id = fields.Many2one('rent.config.property.maintenance.types', string='نوع الصيانة')
    property_id = fields.Many2one(comodel_name='rent.property', string='Property')
    