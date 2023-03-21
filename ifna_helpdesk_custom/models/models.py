from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class HelpDeskCustom(models.Model):
    _inherit = 'helpdesk.ticket'

    user_id = fields.Many2one(
        'res.users', string='Assigned to', compute='_compute_user_and_stage_ids', store=True,
        readonly=False, tracking=True)

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='الحساب التحليلي', store=True, related="product_id.analytic_account",
        tracking=True)
    property_id = fields.Many2one('rent.property', string='عمارة', copy=True,
                                  related="product_id.property_id")

    @api.onchange('partner_id')
    def _get_partner_products(self):
        for i in self:
            products = (
                self.env['sale.order'].search([('partner_id', '=', self.partner_id.id)]).mapped('order_line')).mapped(
                'product_id')
            # fees_amount = sum(self.sale_order_id.order_line.mapped(type))
            if products:
                if len(products) > 1:
                    print("..................", products)
                    return {'domain': {'product_id': [('id', 'in', products.ids)]}}
                else:
                    product_id = self.env["product.product"].browse(products[0])
                    print("..................", product_id)
                    self.product_id = product_id.id


class HelpDeskCustomType(models.Model):
    _inherit = 'helpdesk.ticket.type'

    helpdesk_teams_ids = fields.Many2many(comodel_name="helpdesk.team", relation="rel_team_type",
                                          string="Helpdesk Team", )
