from odoo import api, fields, models, _
from odoo.tools import float_compare, is_html_empty
from odoo.exceptions import UserError, ValidationError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    product_repair = fields.Many2one('product.product', string='Product to Repair')
    compound_id = fields.Many2one('rent.property', string='Compound', tracking=True)
    user_id = fields.Many2one('res.users', string='Assigned to', tracking=True)


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_repair = fields.Many2one('product.product', string='Product to Repair')
    compound_id = fields.Many2one('rent.property', string='Compound', tracking=True)

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id,
                                       credit_account_id, description):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()
        debit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'analytic_account_id': self.product_repair.product_tmpl_id.analytic_account.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
        }

        credit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
        }

        rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(
                    _('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
        return rslt


class HelpDeskCustom(models.Model):
    _inherit = 'repair.order'

    compound_id = fields.Many2one('rent.property', string='Compound', related="product_id.property_id", tracking=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='الحساب التحليلي', related="product_id.product_tmpl_id.analytic_account",
        tracking=True)

    def action_repair_done(self):
        """ Creates stock move for operation and stock move for final product of repair order.
        @return: Move ids of final products

        """
        if self.filtered(lambda repair: not repair.repaired):
            raise UserError(_("Repair must be repaired in order to make the product moves."))
        self._check_company()
        self.operations._check_company()
        self.fees_lines._check_company()
        res = {}
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        Move = self.env['stock.move']
        for repair in self:
            # Try to create move with the appropriate owner
            owner_id = False
            available_qty_owner = self.env['stock.quant']._get_available_quantity(repair.product_id, repair.location_id,
                                                                                  repair.lot_id,
                                                                                  owner_id=repair.partner_id,
                                                                                  strict=True)
            if float_compare(available_qty_owner, repair.product_qty, precision_digits=precision) >= 0:
                owner_id = repair.partner_id.id

            moves = self.env['stock.move']
            for operation in repair.operations:
                move = Move.create({
                    'name': repair.name,
                    'product_id': operation.product_id.id,
                    'product_repair': repair.product_id.id,
                    'product_uom_qty': operation.product_uom_qty,
                    'product_uom': operation.product_uom.id,
                    'partner_id': repair.address_id.id,
                    'location_id': operation.location_id.id,
                    'location_dest_id': operation.location_dest_id.id,
                    'repair_id': repair.id,
                    'origin': repair.name,
                    'company_id': repair.company_id.id,
                })

                # Best effort to reserve the product in a (sub)-location where it is available
                product_qty = move.product_uom._compute_quantity(
                    operation.product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')
                available_quantity = self.env['stock.quant']._get_available_quantity(
                    move.product_id,
                    move.location_id,
                    lot_id=operation.lot_id,
                    strict=False,
                )
                move._update_reserved_quantity(
                    product_qty,
                    available_quantity,
                    move.location_id,
                    lot_id=operation.lot_id,
                    strict=False,
                )
                # Then, set the quantity done. If the required quantity was not reserved, negative
                # quant is created in operation.location_id.
                move._set_quantity_done(operation.product_uom_qty)

                if repair.product_id:
                    move.move_line_ids.product_repair = repair.product_id.id
                    move.move_line_ids.compound_id = repair.compound_id.id
                    move.move_line_ids.user_id = repair.ticket_id.user_id.id
                if operation.lot_id:
                    move.move_line_ids.lot_id = operation.lot_id

                moves |= move
                operation.write({'move_id': move.id, 'state': 'done'})
            move = Move.create({
                'name': repair.name,
                'product_id': repair.product_id.id,
                'product_uom': repair.product_uom.id or repair.product_id.uom_id.id,
                'product_uom_qty': repair.product_qty,
                'partner_id': repair.address_id.id,
                'location_id': repair.location_id.id,
                'location_dest_id': repair.location_id.id,
                'move_line_ids': [(0, 0, {'product_id': repair.product_id.id,
                                          'product_repair': repair.product_id.id,
                                          'user_id': repair.ticket_id.user_id.id,
                                          'compound_id': repair.compound_id.id,
                                          'lot_id': repair.lot_id.id,
                                          'product_uom_qty': 0,  # bypass reservation here
                                          'product_uom_id': repair.product_uom.id or repair.product_id.uom_id.id,
                                          'qty_done': repair.product_qty,
                                          'package_id': False,
                                          'result_package_id': False,
                                          'owner_id': owner_id,
                                          'location_id': repair.location_id.id,  # TODO: owner stuff
                                          'company_id': repair.company_id.id,
                                          'location_dest_id': repair.location_id.id, })],
                'repair_id': repair.id,
                'origin': repair.name,
                'company_id': repair.company_id.id,
            })
            consumed_lines = moves.mapped('move_line_ids')
            produced_lines = move.move_line_ids
            moves |= move
            moves._action_done()
            produced_lines.write({'consume_line_ids': [(6, 0, consumed_lines.ids)]})
            res[repair.id] = move.id
        return res


class HelpDeskCustom(models.Model):
    _inherit = 'helpdesk.ticket'

    user_id = fields.Many2one(
        'res.users', string='Assigned to', compute='_compute_user_and_stage_ids', store=True,
        readonly=False, tracking=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='الحساب التحليلي', related="product_id.product_tmpl_id.analytic_account",
        tracking=True)
    property_id = fields.Many2one('rent.property', string='عمارة', copy=True,
                                  related="product_id.property_id")
    ticket_name = fields.Char("")

    def name_get(self):
        result = []
        for ticket in self:
            result.append((ticket.id, "%s (#%d)" % (ticket.name, ticket._origin.id)))
            ticket.ticket_name = ("%s (#%d)" % (ticket.name, ticket._origin.id))
        return result

    @api.onchange('partner_id')
    def _get_partner_products(self):
        for i in self:
            products = (
                self.env['sale.order'].search([('partner_id', '=', self.partner_id.id)]).mapped('order_line')).mapped(
                'product_id')
            if products:
                if len(products) > 1:
                    return {'domain': {'product_id': [('id', 'in', products.ids)]}}
                else:
                    product_id = self.env["product.product"].browse(products[0])
                    self.product_id = product_id.id
                return {'domain': {'product_id': [('id', 'in', products.ids)]}}
            else:
                return {'domain': {'product_id': [(1, '=', 1)]}}


class HelpDeskCustomType(models.Model):
    _inherit = 'helpdesk.ticket.type'

    helpdesk_teams_ids = fields.Many2many(comodel_name="helpdesk.team", relation="rel_team_type",
                                          string="Helpdesk Team", )
