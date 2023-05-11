# _*_ coding: utf-8
from datetime import datetime
from odoo import models, fields, api, _
import logging

DATE_DICT = {
    '%m/%d/%Y': 'mm/dd/yyyy',
    '%Y/%m/%d': 'yyyy/mm/dd',
    '%m/%d/%y': 'mm/dd/yy',
    '%d/%m/%Y': 'dd/mm/yyyy',
    '%d/%m/%y': 'dd/mm/yy',
    '%d-%m-%Y': 'dd-mm-yyyy',
    '%d-%m-%y': 'dd-mm-yy',
    '%m-%d-%Y': 'mm-dd-yyyy',
    '%m-%d-%y': 'mm-dd-yy',
    '%Y-%m-%d': 'yyyy-mm-dd',
    '%f/%e/%Y': 'm/d/yyyy',
    '%f/%e/%y': 'm/d/yy',
    '%e/%f/%Y': 'd/m/yyyy',
    '%e/%f/%y': 'd/m/yy',
    '%f-%e-%Y': 'm-d-yyyy',
    '%f-%e-%y': 'm-d-yy',
    '%e-%f-%Y': 'd-m-yyyy',
    '%e-%f-%y': 'd-m-yy'
}


class InsTrialBalanceXlsx(models.AbstractModel):
    _name = 'report.account_dynamic_edited.ins_trial_balance_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _logger = logging.getLogger(__name__)
    try:
        _inherit = 'report.report_xlsx.abstract'
    except ImportError:
        _logger.debug('Cannot find report_xlsx module for version 11')

    def convert_to_date(self, datestring=False):
        if datestring:
            lang = self.env.user.lang
            language_id = self.env['res.lang'].search([('code', '=', lang)])[0]
            datestring = fields.Date.from_string(datestring).strftime(language_id.date_format)
            return datetime.strptime(datestring, language_id.date_format)
        else:
            return False

    def generate_xlsx_report(self, workbook, data, record):
        # self._define_formats(workbook)
        """ Add cell formats to current workbook.
                Available formats:
                 * format_title
                 * format_header
                """
        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
        })
        format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font': 'Arial',
            # 'border': True
        })
        format_merged_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'right': True,
            'left': True,
            'font': 'Arial',
        })
        format_merged_header_without_border = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })
        content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'font': 'Arial',
        })
        line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })
        line_header_total = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
            'top': True,
            'bottom': True,
        })
        line_header_left_total = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
            'top': True,
            'bottom': True,
        })
        line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })
        line_header_light_total = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
            'top': True,
            'bottom': True,
        })
        line_header_light_left = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
        })
        line_header_highlight = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
        })
        line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })

        sheet = workbook.add_worksheet('General Ledger')
        sheet_2 = workbook.add_worksheet('Filters')
        sheet.set_column(0, 0, 30)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)

        sheet_2.set_column(0, 0, 35)
        sheet_2.set_column(1, 1, 25)
        sheet_2.set_column(2, 2, 25)
        sheet_2.set_column(3, 3, 25)
        sheet_2.set_column(4, 4, 25)
        sheet_2.set_column(5, 5, 25)
        sheet_2.set_column(6, 6, 25)

        sheet.freeze_panes(5, 0)

        sheet.set_zoom(80)

        sheet.screen_gridlines = False
        sheet_2.screen_gridlines = False
        sheet_2.protect()
        # For Formating purpose
        lang = self.env.user.lang
        lang_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        currency_id = self.env.user.company_id.currency_id

        line_header.num_format = currency_id.excel_format

        line_header_light.num_format = currency_id.excel_format

        line_header_highlight.num_format = currency_id.excel_format

        line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        format_merged_header_without_border.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

        if record:
            data = record.read()
            sheet.merge_range(0, 0, 0, 10, 'Trial Balance' + ' - ' + data[0]['company_id'][1], format_title)
            filter, acc_lines, retained, subtotal = record.get_report_datas()

            row_pos_2 = 0
            row_pos_2 += 2
            if filter:
                # Date from
                sheet_2.write_string(row_pos_2, 0, _('Date from'),
                                     format_header)
                sheet_2.write_datetime(row_pos_2, 1, self.convert_to_date(str(filter['date_from']) or ''),
                                       line_header_light_date)
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Date to'),
                                     format_header)
                sheet_2.write_datetime(row_pos_2, 1, self.convert_to_date(str(filter['date_to']) or ''),
                                       line_header_light_date)

                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Display accounts'),
                                     format_header)
                sheet_2.write_string(row_pos_2, 1, filter['display_accounts'],
                                     content_header)

                # Journals
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Journals'),
                                     format_header)
                j_list = ', '.join([lt or '' for lt in filter.get('journals')])
                sheet_2.write_string(row_pos_2, 1, j_list,
                                     content_header)

                # Accounts
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Analytic Accounts'),
                                     format_header)
                a_list = ', '.join([lt or '' for lt in filter.get('analytics')])
                sheet_2.write_string(row_pos_2, 1, a_list,
                                     content_header)

            row_pos = 0
            row_pos += 3
            sheet.merge_range(row_pos, 1, row_pos, 3, 'Initial Balance', format_merged_header)

            sheet.write_datetime(row_pos, 4, self.convert_to_date(filter.get('date_from')),
                                 format_merged_header_without_border)
            sheet.write_string(row_pos, 5, _(' To '),
                               format_merged_header_without_border)
            sheet.write_datetime(row_pos, 6, self.convert_to_date(filter.get('date_to')),
                                 format_merged_header_without_border)

            sheet.merge_range(row_pos, 7, row_pos, 9, 'Ending Balance', format_merged_header)

            row_pos += 1

            if filter.get('group_level'):
                sheet.write_string(row_pos, 0, _('Account Group'),
                                   format_header)
            else:
                sheet.write_string(row_pos, 0, _('Account'),
                                   format_header)
            # sheet.write_string(row_pos, 0, _('Account'),
            #                    format_header)
            sheet.write_string(row_pos, 1, _('Debit'),
                               format_header)
            sheet.write_string(row_pos, 2, _('Credit'),
                               format_header)
            sheet.write_string(row_pos, 3, _('Balance'),
                               format_header)
            sheet.write_string(row_pos, 4, _('Debit'),
                               format_header)
            sheet.write_string(row_pos, 5, _('Credit'),
                               format_header)
            sheet.write_string(row_pos, 6, _('Balance'),
                               format_header)
            sheet.write_string(row_pos, 7, _('Debit'),
                               format_header)
            sheet.write_string(row_pos, 8, _('Credit'),
                               format_header)
            sheet.write_string(row_pos, 9, _('Balance'),
                               format_header)

            if acc_lines:
                if not filter.get('show_hierarchy'):
                    for line in acc_lines:  # Normal lines
                        row_pos += 1
                        sheet.write_string(row_pos, 0, acc_lines[line].get('code') + ' ' + acc_lines[line].get('name'),
                                           line_header_light_left)
                        sheet.write_number(row_pos, 1, float(acc_lines[line].get('initial_debit')), line_header_light)
                        sheet.write_number(row_pos, 2, float(acc_lines[line].get('initial_credit')), line_header_light)
                        sheet.write_number(row_pos, 3, float(acc_lines[line].get('initial_balance')),
                                           line_header_highlight)
                        sheet.write_number(row_pos, 4, float(acc_lines[line].get('debit')), line_header_light)
                        sheet.write_number(row_pos, 5, float(acc_lines[line].get('credit')), line_header_light)
                        sheet.write_number(row_pos, 6, float(acc_lines[line].get('balance')), line_header_highlight)
                        sheet.write_number(row_pos, 7, float(acc_lines[line].get('ending_debit')), line_header_light)
                        sheet.write_number(row_pos, 8, float(acc_lines[line].get('ending_credit')), line_header_light)
                        sheet.write_number(row_pos, 9, float(acc_lines[line].get('ending_balance')),
                                           line_header_highlight)
                else:
                    for line in acc_lines:  # Normal lines
                        row_pos += 1
                        blank_space = '   ' * len(line.get('indent_list'))
                        if line.get('dummy'):
                            sheet.write_string(row_pos, 0, blank_space + line.get('code'),
                                               line_header_light_left)
                        else:
                            sheet.write_string(row_pos, 0, blank_space + line.get('code') + ' ' + line.get('name'),
                                               line_header_light_left)
                        sheet.write_number(row_pos, 1, float(line.get('initial_debit')), line_header_light)
                        sheet.write_number(row_pos, 2, float(line.get('initial_credit')), line_header_light)
                        sheet.write_number(row_pos, 3, float(line.get('initial_balance')), line_header_highlight)
                        sheet.write_number(row_pos, 4, float(line.get('debit')), line_header_light)
                        sheet.write_number(row_pos, 5, float(line.get('credit')), line_header_light)
                        sheet.write_number(row_pos, 6, float(line.get('balance')), line_header_highlight)
                        sheet.write_number(row_pos, 7, float(line.get('ending_debit')), line_header_light)
                        sheet.write_number(row_pos, 8, float(line.get('ending_credit')), line_header_light)
                        sheet.write_number(row_pos, 9, float(line.get('ending_balance')), line_header_highlight)

                if filter.get('strict_range') and not filter.get('group_level'):
                    # Retained Earnings line
                    row_pos += 1
                    sheet.write_string(row_pos, 0, '        ' + retained['RETAINED'].get('name'),
                                       line_header_light_left)
                    sheet.write_number(row_pos, 1, float(retained['RETAINED'].get('initial_debit')), line_header_light)
                    sheet.write_number(row_pos, 2, float(retained['RETAINED'].get('initial_credit')), line_header_light)
                    sheet.write_number(row_pos, 3, float(retained['RETAINED'].get('initial_balance')),
                                       line_header_highlight)
                    sheet.write_number(row_pos, 4, float(retained['RETAINED'].get('debit')), line_header_light)
                    sheet.write_number(row_pos, 5, float(retained['RETAINED'].get('credit')), line_header_light)
                    sheet.write_number(row_pos, 6, float(retained['RETAINED'].get('balance')), line_header_highlight)
                    sheet.write_number(row_pos, 7, float(retained['RETAINED'].get('ending_debit')), line_header_light)
                    sheet.write_number(row_pos, 8, float(retained['RETAINED'].get('ending_credit')), line_header_light)
                    sheet.write_number(row_pos, 9, float(retained['RETAINED'].get('ending_balance')),
                                       line_header_highlight)
                # Sub total line
                row_pos += 2
                sheet.write_string(row_pos, 0,
                                   subtotal['SUBTOTAL'].get('code') + ' ' + subtotal['SUBTOTAL'].get('name'),
                                   line_header_left_total)
                sheet.write_number(row_pos, 1, float(subtotal['SUBTOTAL'].get('initial_debit')),
                                   line_header_light_total)
                sheet.write_number(row_pos, 2, float(subtotal['SUBTOTAL'].get('initial_credit')),
                                   line_header_light_total)
                sheet.write_number(row_pos, 3, float(subtotal['SUBTOTAL'].get('initial_balance')), line_header_total)
                sheet.write_number(row_pos, 4, float(subtotal['SUBTOTAL'].get('debit')), line_header_light_total)
                sheet.write_number(row_pos, 5, float(subtotal['SUBTOTAL'].get('credit')), line_header_light_total)
                sheet.write_number(row_pos, 6, float(subtotal['SUBTOTAL'].get('balance')), line_header_total)
                sheet.write_number(row_pos, 7, float(subtotal['SUBTOTAL'].get('ending_debit')), line_header_light_total)
                sheet.write_number(row_pos, 8, float(subtotal['SUBTOTAL'].get('ending_credit')),
                                   line_header_light_total)
                sheet.write_number(row_pos, 9, float(subtotal['SUBTOTAL'].get('ending_balance')), line_header_total)
