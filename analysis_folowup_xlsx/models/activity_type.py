from odoo import api, fields, models, _
from odoo import exceptions
import calendar

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class UpdateTenants(models.TransientModel):
    _name = 'tenants.report.wizard'

    def print_xlsx_report(self):
        rec = self.env.ref('analysis_folowup_xlsx.report_update_tenants_xlsx').report_action(self)
        return rec


##########################################################
class UpdateTenantsReport(models.AbstractModel):
    _name = 'report.analysis_folowup_xlsx.print_tenants_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        worksheet = workbook.add_worksheet('Update Tenants Report')
        # worksheet.right_to_left()

        header_format2 = workbook.add_format({
            'font_size': 18,
            'border': 1,
            'align': 'center',
            'font_color': 'black',
            'bold': True,
            'valign': 'vcenter',
            'border_color': 'black',
            'fg_color': '#C0C0C0'})
        cell_text_format = workbook.add_format({'align': 'center','valign': 'vcenter', 'bold': True, 'size': 12, 'fg_color': '#C0C0C0'})
        cell_body_table = workbook.add_format({'align': 'center', 'size': 12})

        worksheet.merge_range('C1:E1', 'Update Tenants Report', header_format2)

        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 23)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('H:H', 18)
        worksheet.set_column('I:I', 25)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 18)
        worksheet.set_column('L:L', 18)
        worksheet.set_column('M:M', 15)
        worksheet.set_column('N:N', 15)
        worksheet.set_column('O:O', 20)
        worksheet.set_column('P:P', 15)
        worksheet.set_column('Q:Q', 15)
        worksheet.set_column('R:R', 15)
        worksheet.set_column('S:S', 15)
        worksheet.set_column('T:T', 15)
        worksheet.set_column('U:U', 15)
        worksheet.set_column('V:V', 15)
        worksheet.set_column('W:W', 15)
        worksheet.set_column('X:X', 15)
        worksheet.set_column('Y:Y', 15)
        worksheet.set_column('AA:AA', 15)
        worksheet.set_column('AB:AB', 15)
        worksheet.set_column('AC:AC', 15)
        worksheet.set_column('AD:AD', 15)
        worksheet.set_column('AE:AE', 15)
        worksheet.set_column('AF:AF', 15)
        worksheet.set_column('AG:AG', 22)

        domain = []
        worksheet.set_row(0, 40)
        worksheet.set_row(2, 25)
        worksheet.set_row(4, 50)
        # worksheet.set_row(6, 50)

        # Table Header:
        worksheet.write(4, 0, 'Comp', cell_text_format)
        worksheet.write(4, 1, 'Villa/  Apt.', cell_text_format)
        worksheet.write(4, 2, '*Style/No. of Bed Rooms', cell_text_format)
        worksheet.write(4, 3, 'FF /UF/SF', cell_text_format)
        worksheet.write(4, 4, 'Tenant Name', cell_text_format)
        worksheet.write(4, 5, 'Nationality', cell_text_format)
        worksheet.write(4, 6, 'Work/Company', cell_text_format)
        worksheet.write(4, 7, 'Mobile', cell_text_format)
        worksheet.write(4, 8, 'Email', cell_text_format)
        worksheet.write(4, 9, 'Lease Commencement Date', cell_text_format)
        worksheet.write(4, 10, 'Contract Year', cell_text_format)
        worksheet.write(4, 11, 'Contract Month', cell_text_format)
        worksheet.write(4, 12, 'Rent Value', cell_text_format)
        worksheet.write(4, 13, 'Admin Fee', cell_text_format)
        worksheet.write(4, 14, 'Security deposit', cell_text_format)
        worksheet.write(4, 15, 'Terms', cell_text_format)
        worksheet.write(4, 16, 'JAN ', cell_text_format)
        worksheet.write(4, 17, 'FEB ', cell_text_format)
        worksheet.write(4, 18, 'MAR', cell_text_format)
        worksheet.write(4, 19, 'APR ', cell_text_format)
        worksheet.write(4, 20, 'MAY ', cell_text_format)
        worksheet.write(4, 21, 'JUN ', cell_text_format)
        worksheet.write(4, 22, 'JUL ', cell_text_format)
        worksheet.write(4, 23, 'AUG ', cell_text_format)
        worksheet.write(4, 24, 'SEP ', cell_text_format)
        worksheet.write(4, 25, 'OCT ', cell_text_format)
        worksheet.write(4, 26, 'NOV ', cell_text_format)
        worksheet.write(4, 27, 'DEC ', cell_text_format)
        worksheet.write(4, 28, 'Expected Income', cell_text_format)
        worksheet.write(4, 29, 'EJAR', cell_text_format)
        worksheet.write(4, 30, 'Remarks', cell_text_format)
        worksheet.write(4, 31, 'File Completed', cell_text_format)
        worksheet.write(4, 32, 'updated/ invoiced', cell_text_format)

        domain = [
            ('state', 'not in', ('draft', 'sent')),
            ('is_rental_order', '=', True)
        ]

        items = self.env['sale.order'].search(domain)
        # Products: Table Body:
        row = 5
        for i in items:

            # for line in i.order_line.filtered(lambda s: s.product_id.detailed_type != "service"):
            for line in i.order_line.filtered(lambda s: s.product_id.rent_ok == True):

                services = i.order_line.filtered(lambda s: s.product_id.rent_ok == False)
                admin = sum(
                    services.filtered(lambda s: s.product_id.product_tmpl_id.fees_type == "admin").mapped('price_unit'))
                security = sum(services.filtered(lambda s: s.product_id.product_tmpl_id.fees_type == "security").mapped(
                    'price_unit'))

                column = 0
                worksheet.write(row, column, line.property_number.property_name, cell_body_table)
                worksheet.write(row, column + 1, line.product_id.name, cell_body_table)
                worksheet.write(row, column + 2, line.product_id.rent_config_unit_type_id.unit_type_name,
                                cell_body_table)
                worksheet.write(row, column + 3, line.product_id.rent_config_unit_purpose_id.unit_purpose_name,
                                cell_body_table)
                worksheet.write(row, column + 4, i.partner_id.name, cell_body_table)
                worksheet.write(row, column + 5, i.partner_id.country_id.name or " ", cell_body_table)
                worksheet.write(row, column + 6, i.partner_id.parent_id.name or " ", cell_body_table)
                worksheet.write(row, column + 7, i.partner_id.mobile or " ", cell_body_table)
                worksheet.write(row, column + 8, i.partner_id.email or " ", cell_body_table)
                worksheet.write(row, column + 9, str(i.date_order), cell_body_table)
                worksheet.write(row, column + 10, calendar.month_name[i.date_order.month], cell_body_table)
                worksheet.write(row, column + 11, str(i.date_order.year), cell_body_table)
                worksheet.write(row, column + 12, line.price_subtotal or " ", cell_body_table)
                worksheet.write(row, column + 13, admin or " ", cell_body_table)
                worksheet.write(row, column + 14, security or " ", cell_body_table)
                worksheet.write(row, column + 15, i.invoice_terms or " ", cell_body_table)

                total_invoice = 0
                for j in i.order_contract_invoice:
                    total_invoice += j.amount
                    if j.fromdate.month == 1:
                        worksheet.write(row, column + 16, j.amount or " ", cell_body_table)
                    if j.fromdate.month == 2:
                        worksheet.write(row, column + 17, j.amount or " ", cell_body_table)
                    if j.fromdate.month == 3:
                        worksheet.write(row, column + 18, j.amount or " ", cell_body_table)
                    if j.fromdate.month == 4:
                        worksheet.write(row, column + 19, j.amount or " ", cell_body_table)
                    if j.fromdate.month == 5:
                        worksheet.write(row, column + 20, j.amount or " ", cell_body_table)
                    if j.fromdate.month == 6:
                        worksheet.write(row, column + 21, j.amount or " ", cell_body_table)
                    if j.fromdate.month == 7:
                        worksheet.write(row, column + 22, j.amount or " ", cell_body_table)
                    if j.fromdate.month == 8:
                        worksheet.write(row, column + 23, j.amount or " ", cell_body_table)
                    if j.fromdate.month == 9:
                        worksheet.write(row, column + 24, j.amount or " ", cell_body_table)
                    if j.fromdate.month == 10:
                        worksheet.write(row, column + 25, j.amount or " ", cell_body_table)
                    if j.fromdate.month == 11:
                        worksheet.write(row, column + 26, j.amount or " ", cell_body_table)
                    if j.fromdate.month == 12:
                        worksheet.write(row, column + 27, j.amount or " ", cell_body_table)
                worksheet.write(row, column + 28, total_invoice or " ", cell_body_table)
                worksheet.write(row, column + 29, i.ejar or " ", cell_body_table)
                worksheet.write(row, column + 30, i.remarks_c or " ", cell_body_table)
                worksheet.write(row, column + 31, i.file or " ", cell_body_table)
                worksheet.write(row, column + 32, i.updated_invoices.name or " ", cell_body_table)
                row += 1
