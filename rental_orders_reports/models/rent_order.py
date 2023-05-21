from odoo import models, fields, api, exceptions, _
import datetime, calendar
# from odoo.tools import dateutil
from datetime import date, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class WizRentAddedValue(models.Model):
    _name = "rent.wiz"

    compound_ids = fields.Many2many('rent.property', string='Compound', required=True)
    report_data = fields.One2many('rent.order.report', 'report_id')
    compound_data = fields.One2many('compound.report', 'report_id')
    total_total =fields.Float(compute='cal_total_units')
    total_occupied = fields.Float(compute='cal_total_units')
    total_empty = fields.Float(compute='cal_total_units')

    @api.depends('compound_data')
    def cal_total_units(self):
        for rec in self:
            rec.total_total=0
            rec.total_occupied = 0
            rec.total_empty = 0
            if rec.compound_data:
                for line in rec.compound_data:
                    rec.total_total += line.total
                    rec.total_occupied += line.occupied
                    rec.total_empty += line.empty

    # @api.onchange('compound_ids')
    def fill_temp(self):
        for rec in self:
            list = []
            rec.report_data.unlink()
            if rec.compound_ids:
                rent_orders = self.env['sale.order.line'].search(
                    [('property_number', 'in', rec.compound_ids.ids)])
                property = self.env['rent.property'].search(
                    [('id', 'in', rec.compound_ids.ids)])

                # for item in rec.compound_ids:
                #     list.append(item.id)
                # print(list,'jsakd')

                if rent_orders:
                    for pick in rent_orders:
                        rec.write({
                            'report_data': [(0, 0, {
                                'contract_no': pick.order_id.name,
                                'compound_id': pick.property_number.id,
                                'villa': pick.product_id.id,
                                'partner_id': pick.order_id.partner_id.id,
                                'untaxed_amount': pick.order_id.amount_untaxed,
                                'rent_value': pick.order_id.amount_total,
                                'contract_start_date': pick.order_id.date_str,
                                'return_date': pick.order_id.return_date,
                                'return_reason': pick.order_id.return_reason,

                            })]
                        })

                if property:
                    for prop in property:
                        rec.write({
                            'compound_data': [(0, 0, {
                                'compound_id': prop.id,
                                'total': prop.total_units,
                                'occupied': prop.total_units - prop.free_units,
                                'empty': prop.free_units,

                            })]
                        })

    def download_excel(self):
        self.fill_temp()
        return self.env.ref('rental_orders_reports.rent_order_report').report_action(self)
    # def download_pdf(self):
    #     self.fill_temp()
    #     return self.env.ref('value_added_cost_report.cost_pdf_stock_report').report_action(self)


class RentOrderReportInv(models.Model):
    _name = "rent.order.report"

    contract_no = fields.Char(string='Contract Number')
    compound_id = fields.Many2one('rent.property', string='Compound')
    villa = fields.Many2one('product.product', string='Villa')
    partner_id = fields.Many2one('res.partner', string='Customer')
    untaxed_amount = fields.Float()
    rent_value = fields.Float()
    contract_start_date = fields.Char()
    return_date = fields.Datetime()
    return_reason = fields.Char()

    report_id = fields.Many2one('rent.wiz')


class CompoundRentOrderReportInv(models.Model):
    _name = "compound.report"

    compound_id = fields.Many2one('rent.property', string='Compound')
    total = fields.Float()
    occupied = fields.Float()
    empty = fields.Float()


    report_id = fields.Many2one('rent.wiz')

class PartnerXlsx(models.AbstractModel):
    _name = 'report.rental_orders_reports.rent_order_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet("Summary Tenants Update")
        format = workbook.add_format({'bold': False, 'align': 'center'})
        style = workbook.add_format({'bold': True, 'align': 'center'})
        sheet.write(0, 3, "New Tenants", style)
        sheet.write(1, 0, "Contract Number", style)
        sheet.write(1, 1, "Compound", style)
        sheet.write(1, 2, "Villa", style)
        sheet.write(1, 3, "Customer", style)
        sheet.write(1, 4, "Untaxed Amount", style)
        sheet.write(1, 5, "Rent Value", style)
        sheet.write(1, 6, "Contract Start Date", style)

        line_number = 2
        length = len(partners.report_data)
        # print(length)
        #
        # if partners.time_range=='date':
        for line in partners.report_data:
            #     if length > 0:
            sheet.write(line_number, 0, line.contract_no, format)
            sheet.write(line_number, 1, line.compound_id.property_name, format)
            sheet.write(line_number, 2, line.villa.name, format)
            sheet.write(line_number, 3, line.partner_id.name, format)
            sheet.write(line_number, 4, line.untaxed_amount, format)
            sheet.write(line_number, 5, line.rent_value, format)
            sheet.write(line_number, 6, str(line.contract_start_date), format)

            line_number += 1
            length -= 1

        sheet.write(0, 14, "Tenants Left", style)
        sheet.write(1, 11, "Contract Number", style)
        sheet.write(1, 12, "Compound", style)
        sheet.write(1, 13, "Villa", style)
        sheet.write(1, 14, "Customer", style)
        sheet.write(1, 15, "Return Date", style)
        sheet.write(1, 16, "Return Reason", style)
        line_number = 2
        for line in partners.report_data:
            #     if length > 0:
            sheet.write(line_number, 11, line.contract_no, format)
            sheet.write(line_number, 12, line.compound_id.property_name, format)
            sheet.write(line_number, 13, line.villa.name, format)
            sheet.write(line_number, 14, line.partner_id.name, format)
            sheet.write(line_number, 15, str(line.return_date), format)
            sheet.write(line_number, 16, line.return_reason, format)

            line_number += 1
            length -= 1
        line_no =  line_number+4
        sheet.write(line_number+3, 13, "Units", style)
        sheet.write(line_no, 12, "Compound", style)
        sheet.write(line_no, 13, "Total", style)
        sheet.write(line_no, 14, "occupied", style)
        sheet.write(line_no, 15, "empty", style)

        line_num = line_no+1
        table_length = len(partners.compound_data)
        for line in partners.compound_data:
            #     if length > 0:
            sheet.write(line_num, 12, line.compound_id.property_name, format)
            sheet.write(line_num, 13, line.total, format)
            sheet.write(line_num, 14, line.occupied, format)
            sheet.write(line_num, 15, line.empty, format)


            line_num += 1
            table_length -= 1
        sheet.write(line_num +1, 12, "Total Number Of Units", style)
        sheet.write(line_num+1, 13, partners.total_total, format)
        sheet.write(line_num + 1, 14, partners.total_occupied, format)
        sheet.write(line_num + 1, 15, partners.total_empty, format)


class SaleOrderRentals(models.Model):
    _inherit = 'sale.order'

    date_str = fields.Char(compute='_compute_date_in_string')
    return_reason = fields.Char('Return Reason')
    return_date = fields.Datetime()

    @api.depends('fromdate')
    def _compute_date_in_string(self):
        for rec in self:
            rec.date_str = False
            if rec.fromdate:
                asd = str(rec.fromdate)
                qq = asd.split(' ')
                f = qq[0]
                s = qq[1]
                print(f, s)
                date_only = f.split('-')
                date_time = s.split(':')
                day = date_only[0]
                month = date_only[1]
                year = date_only[2]
                # min = date_time[0]
                # hour = date_time[1]
                # sec = date_time[2]
                mm = month + '/' + year + '/' + day + ' ' + s
                rec.date_str = (mm)



class RentalProcessingRentOrders(models.TransientModel):
    _inherit = 'rental.order.wizard'

    return_reason = fields.Char('Return Reason')

    def apply(self):
        res=super(RentalProcessingRentOrders,self).apply()
        self.order_id.return_reason = self.return_reason
        self.order_id.return_date = fields.Datetime.now()
        return res


class RentPropertyRentals(models.Model):
    _inherit = 'rent.property'

    total_units = fields.Float(compute='cal_total_units')

    @api.depends('unit_ids')
    def cal_total_units(self):
        for rec in self:
            rec.total_units =0
            if rec.unit_ids:
                rec.total_units = len(rec.unit_ids)
            else:
                rec.total_units =0
#
# class PartnerXlsx(models.AbstractModel):
#     _name = 'report.rental_orders_reports.rent_order_report_xlsx'
#     _inherit = 'report.report_xlsx.abstract'
#
#     def generate_xlsx_report(self, workbook, data, partners):
#         sheet = workbook.add_worksheet("Summary Tenants Update")
#         format = workbook.add_format({'bold': False, 'align': 'center'})
#         style = workbook.add_format({'bold': True, 'align': 'center'})
#         sheet.write(0, 3, "New Tenants", style)
#         sheet.write(1, 0, "Contract Number", style)
#         sheet.write(1, 1, "Compound", style)
#         sheet.write(1, 2, "Villa", style)
#         sheet.write(1, 3, "Customer", style)
#         sheet.write(1, 4, "Untaxed Amount", style)
#         sheet.write(1, 5, "Rent Value", style)
#         sheet.write(1, 6, "Contract Start Date", style)
#
#         line_number = 2
#         length = len(partners.order_line)
#         # print(length)
#         #
#         # if partners.time_range=='date':
#         for line in partners.order_line:
#             #     if length > 0:
#             sheet.write(line_number, 0, line.order_id.name, format)
#             sheet.write(line_number, 1, line.property_number.property_name, format)
#             sheet.write(line_number, 2, line.product_id.name, format)
#             sheet.write(line_number, 3, line.order_id.partner_id.name, format)
#             sheet.write(line_number, 4, line.order_id.amount_untaxed, format)
#             sheet.write(line_number, 5, line.order_id.amount_total, format)
#             sheet.write(line_number, 6, str(line.order_id.date_str), format)
#
#             line_number += 1
#             length -= 1
#         # sheet.write(line_number, 0, line.footer_collection, format)
