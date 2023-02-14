
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    deviation_amount  = fields.Float(string='Deviation Amount', 
        compute='_compute_deviation_amount', store=True, readonly=True)
    deviation_ratio  = fields.Float(string='Deviation Ratio', 
        compute='_compute_deviation_ratio', store=True, readonly=True)
    
    @api.depends('planned_amount', 'practical_amount')
    def _compute_deviation_amount(self):
        for record in self:
            record.deviation_amount = record.planned_amount + record.practical_amount
            
    @api.depends('deviation_amount', 'planned_amount')
    def _compute_deviation_ratio(self):
        for line in self:
            if line.planned_amount != 0.00:
                line.deviation_ratio = float(line.deviation_amount / line.planned_amount)
            else:
                line.deviation_ratio = 0.00
                
    

    
