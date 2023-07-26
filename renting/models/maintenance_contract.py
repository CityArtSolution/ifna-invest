# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceContract(models.Model):
    _name = 'maintenance.contract'
    _description = 'Maintenance Contract'

    vendor_id = fields.Many2one('res.partner', string='شركة الصيانة')
    attachment_id = fields.Many2many(comodel_name='ir.attachment', string='عقد الصيانة')

    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    visits = fields.Integer(string='Number of visits')
    visits_ids = fields.Many2many('ir.attachment', 'visit_ir_attachments_rel', 'visit_id', 'attachment_id',
                                  string='Visits attachments')
    maintenance_type_id = fields.Many2one('rent.config.property.maintenance.types', string='نوع الصيانة')
    property_id = fields.Many2one(comodel_name='rent.property', string='Property')
