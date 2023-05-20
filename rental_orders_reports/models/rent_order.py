from odoo import models, fields, api, exceptions, _
import datetime, calendar
# from odoo.tools import dateutil
from datetime import date, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

#
# class WizCostStockAddedValue(models.Model):
#     _name = "cost.wiz"
#
#     picking_id = fields.Many2one('stock.picking', string='رقم الشحنة', required=True)
#     po_id = fields.Many2one('purchase.order', string='رقم امر المشتريات')
#
#     report_data = fields.One2many('cost.stock.report', 'report_id')
#
#     # @api.onchange('picking_id')
#     def fill_temp(self):
#         for rec in self:
#             rec.report_data.unlink()
#             if rec.po_id:
#                 all_pickings = self.env['stock.picking'].search(
#                     [('id', '=', rec.picking_id.id), ('origin', '=', rec.po_id.name)])
#             else:
#                 all_pickings = self.env['stock.picking'].search(
#                     [('id', '=', rec.picking_id.id)])
#                 po = self.env['purchase.order'].search(
#                     [('name', '=', rec.picking_id.origin)])
#                 if po:
#                     rec.po_id = po.id
#
#             if all_pickings:
#                 for pick in all_pickings:
#                     if pick.move_ids_without_package:
#                         for line in pick.move_ids_without_package:
#                             rec.write({
#                                 'report_data': [(0, 0, {
#                                     'picking_id': rec.picking_id.id,
#                                     'po_id': pick.origin,
#                                     'item': line.product_id.id,
#                                     'code_item': line.product_id.barcode,
#                                     'ordered_qty': line.product_uom_qty,
#                                     'delivered_qty': line.quantity_done,
#                                     # 'unit_cost': line.unit_type_id,
#
#                                 })]
#                             })
#             if rec.po_id.order_line:
#                 for order_po in rec.po_id.order_line:
#                     for wiz in rec.report_data:
#                         if (wiz.item.id == order_po.product_id.id) and (wiz.ordered_qty == order_po.product_qty):
#                             wiz.unit_cost = order_po.price_unit
#
#     def download_excel(self):
#         self.fill_temp()
#         return self.env.ref('value_added_cost_report.cost_stock_report').report_action(self)
#     def download_pdf(self):
#         self.fill_temp()
#         return self.env.ref('value_added_cost_report.cost_pdf_stock_report').report_action(self)


# class CostStockReportInv(models.Model):
#     _name = "cost.stock.report"
#
#     picking_id = fields.Many2one('stock.picking', string='Order Number')
#     po_id = fields.Char(string='Po Number')
#     code_item = fields.Char()
#     item = fields.Many2one('product.product')
#     ordered_qty = fields.Float()
#     delivered_qty = fields.Float()
#     unit_cost = fields.Float()
#
#     report_id = fields.Many2one('cost.wiz')

class SaleOrderRentals(models.Model):
    _inherit = 'sale.order'

    date_str = fields.Char(compute='_compute_date_in_string')

    @api.depends('fromdate')
    def _compute_date_in_string(self):
        for rec in self:
            rec.date_str=False
            if rec.fromdate:
                asd = str(rec.fromdate)
                qq = asd.split(' ')
                f = qq[0]
                s = qq[1]
                print(f,s)
                date_only = f.split('-')
                date_time = s.split(':')
                day = date_only[0]
                month = date_only[1]
                year = date_only[2]
                # min = date_time[0]
                # hour = date_time[1]
                # sec = date_time[2]
                mm = month +'/'+ year+'/' + day+' '+s
                rec.date_str = (mm)


class PartnerXlsx(models.AbstractModel):
    _name = 'report.rental_orders_reports.rent_order_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet("Summary Tenants Update")
        format = workbook.add_format({'bold': False, 'align': 'center'})
        style = workbook.add_format({'bold': True, 'align': 'center'})
        sheet.write(0, 3, "New Tenants",style)
        sheet.write(1, 0, "Contract Number", style)
        sheet.write(1, 1, "Compound", style)
        sheet.write(1, 2, "Villa", style)
        sheet.write(1, 3, "Customer", style)
        sheet.write(1, 4, "Untaxed Amount", style)
        sheet.write(1, 5, "Rent Value", style)
        sheet.write(1, 6, "Contract Start Date", style)

        line_number = 2
        length = len(partners.order_line)
        # print(length)
        #
        # if partners.time_range=='date':
        for line in partners.order_line:
            #     if length > 0:
            sheet.write(line_number, 0, line.order_id.name, format)
            sheet.write(line_number, 1, line.property_number.property_name, format)
            sheet.write(line_number, 2, line.product_id.name, format)
            sheet.write(line_number, 3, line.order_id.partner_id.name, format)
            sheet.write(line_number, 4, line.order_id.amount_untaxed, format)
            sheet.write(line_number, 5, line.order_id.amount_total, format)
            sheet.write(line_number, 6, str(line.order_id.date_str), format)

            line_number += 1
            length -= 1
        # sheet.write(line_number, 0, line.footer_collection, format)
