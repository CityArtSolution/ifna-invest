from odoo import models, fields, api


class LegalAccountMoveInherit(models.Model):
    _inherit = 'account.move'

    case_id = fields.Many2one('legal.case', 'Case', tracking=True)

    @api.model
    def create(self, vals):
        print("Context in create:", self.env.context)
        return super(LegalAccountMoveInherit, self).create(vals)
