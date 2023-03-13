# _*_ coding: utf-8
import logging
from datetime import datetime
from odoo import models, fields, api, _

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


class InsPartnerAgeingXlsx(models.AbstractModel):
    _name = 'report.account_dynamic_edited.ins_partner_ageing_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _logger = logging.getLogger(__name__)
    try:
        _inherit = 'report.report_xlsx.abstract'
    except ImportError:
        _logger.debug('Cannot find report_xlsx module for version 11')

        # def _define_formats(self, workbook):

        # def prepare_report_filters(self, filter):

        # def prepare_report_contents(self, data, period_dict, period_list, ageing_lines, filter):

    # def _format_float_and_dates(self, currency_id, lang_id):

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
            'font_size': 14,
            'font': 'Arial'
        })
        format_header = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'align': 'center',
            'font': 'Arial'
            # 'border': True
        })
        format_header_period = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'align': 'center',
            'font': 'Arial',
            'left': True,
            'right': True,
            # 'border': True
        })
        content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial'
        })
        content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial'
            # 'num_format': 'dd/mm/yyyy',
        })
        line_header = workbook.add_format({
            'font_size': 11,
            'align': 'center',
            'bold': True,
            'left': True,
            'right': True,
            'font': 'Arial'
        })
        line_header_total = workbook.add_format({
            'font_size': 11,
            'align': 'center',
            'bold': True,
            'border': True,
            'font': 'Arial'
        })
        line_header_period = workbook.add_format({
            'font_size': 11,
            'align': 'center',
            'bold': True,
            'left': True,
            'right': True,
            'font': 'Arial'
        })
        line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'border': False,
            'font': 'Arial',
            'text_wrap': True,
        })
        line_header_light_period = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'left': True,
            'right': True,
            'font': 'Arial',
            'text_wrap': True,
        })
        line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'border': False,
            'font': 'Arial',
            'align': 'center',
        })

        row_pos = 0
        row_pos_2 = 0

        record = record  # Wizard object

        sheet = workbook.add_worksheet('Partner Ageing')

        sheet_2 = workbook.add_worksheet('Filters')
        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 3, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 15)
        sheet.set_column(11, 11, 15)

        sheet_2.set_column(0, 0, 35)
        sheet_2.set_column(1, 1, 25)
        sheet_2.set_column(2, 2, 25)
        sheet_2.set_column(3, 3, 25)
        sheet_2.set_column(4, 4, 25)
        sheet_2.set_column(5, 5, 25)
        sheet_2.set_column(6, 6, 25)

        sheet.freeze_panes(4, 0)

        sheet.screen_gridlines = False
        sheet_2.screen_gridlines = False
        sheet_2.protect()
        record = record

        sheet.set_zoom(75)

        # For Formating purpose
        lang = self.env.user.lang
        lang_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        # self._format_float_and_dates(self.env.user.company_id.currency_id, self.language_id)
        currency_id = self.env.user.company_id.currency_id
        line_header.num_format = currency_id.excel_format
        line_header_light.num_format = currency_id.excel_format
        line_header_light_period.num_format = currency_id.excel_format
        line_header_total.num_format = currency_id.excel_format
        line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        content_header_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

        if record:
            data = record.read()
            sheet.merge_range(0, 0, 0, 11, 'Partner Ageing' + ' - ' + data[0]['company_id'][1], format_title)
            dateformat = self.env.user.lang
            filter, ageing_lines, period_dict, period_list = record.get_report_datas()
            # Filter section
            # self.prepare_report_filters(filters)
            """It is writing under second page"""
            row_pos_2 = 0
            row_pos_2 += 2
            if filter:
                # Date from
                sheet_2.write_string(row_pos_2, 0, _('As on Date'),
                                          format_header)
                sheet_2.write_datetime(row_pos_2, 1, self.convert_to_date(str(filter['as_on_date']) or ''),
                                            content_header_date)

                # Partners
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Partners'),
                                          format_header)
                p_list = ', '.join([lt or '' for lt in filter.get('partners')])
                sheet_2.write_string(row_pos_2, 1, p_list,
                                          content_header)

                # Partner Tags
                row_pos_2 += 1
                sheet_2.write_string(row_pos_2, 0, _('Partner Tag'),
                                          format_header)
                p_list = ', '.join([lt or '' for lt in filter.get('categories')])
                sheet_2.write_string(row_pos_2, 1, p_list,
                                          content_header)
            # Content section
            # self.prepare_report_contents(data, period_dict, period_list, ageing_lines, filters)
            data = data[0]
            row_pos = 0
            row_pos += 3

            if record.include_details:
                sheet.write_string(row_pos, 0, _('Entry #'), format_header)
                sheet.write_string(row_pos, 1, _('Due Date'), format_header)
                sheet.write_string(row_pos, 2, _('Journal'), format_header)
                sheet.write_string(row_pos, 3, _('Account'), format_header)
            else:
                sheet.merge_range(row_pos, 0, row_pos, 3, _('Partner'),
                                       format_header)
            k = 4
            for period in period_list:
                sheet.write_string(row_pos, k, str(period),
                                        format_header_period)
                k += 1
            sheet.write_string(row_pos, k, _('Total'),
                                    format_header_period)
            if ageing_lines:
                for line in ageing_lines:

                    # Dummy vacant lines
                    row_pos += 1
                    sheet.write_string(row_pos, 4, '', line_header_light_period)
                    sheet.write_string(row_pos, 5, '', line_header_light_period)
                    sheet.write_string(row_pos, 6, '', line_header_light_period)
                    sheet.write_string(row_pos, 7, '', line_header_light_period)
                    sheet.write_string(row_pos, 8, '', line_header_light_period)
                    sheet.write_string(row_pos, 9, '', line_header_light_period)
                    sheet.write_string(row_pos, 10, '', line_header_light_period)
                    sheet.write_string(row_pos, 11, '', line_header_light_period)

                    row_pos += 1
                    if line != 'Total':
                        sheet.merge_range(row_pos, 0, row_pos, 3, ageing_lines[line].get('partner_name'),
                                               line_header)
                    else:
                        sheet.merge_range(row_pos, 0, row_pos, 3, _('Total'), line_header_total)
                    k = 4

                    for period in period_list:
                        if line != 'Total':
                            sheet.write_number(row_pos, k, ageing_lines[line][period], line_header)
                        else:
                            sheet.write_number(row_pos, k, ageing_lines[line][period], line_header_total)
                        k += 1
                    if line != 'Total':
                        sheet.write_number(row_pos, k, ageing_lines[line]['total'], line_header)
                    else:
                        sheet.write_number(row_pos, k, ageing_lines[line]['total'], line_header_total)

                    if record.include_details:
                        if line != 'Total':
                            count, offset, sub_lines, period_list = record.process_detailed_data(partner=line,
                                                                                                      fetch_range=1000000)
                            for sub_line in sub_lines:
                                row_pos += 1
                                sheet.write_string(row_pos, 0, sub_line.get('move_name') or '',
                                                        line_header_light)
                                date = self.convert_to_date(
                                    sub_line.get('date_maturity') and sub_line.get('date_maturity').strftime(
                                        '%Y-%m-%d') or sub_line.get('date').strftime('%Y-%m-%d'))
                                sheet.write_datetime(row_pos, 1, date,
                                                          line_header_light_date)
                                sheet.write_string(row_pos, 2, sub_line.get('journal_name'),
                                                        line_header_light)
                                sheet.write_string(row_pos, 3, sub_line.get('account_name') or '',
                                                        line_header_light)

                                sheet.write_number(row_pos, 4,
                                                        float(sub_line.get('range_0')), line_header_light_period)
                                sheet.write_number(row_pos, 5,
                                                        float(sub_line.get('range_1')), line_header_light_period)
                                sheet.write_number(row_pos, 6,
                                                        float(sub_line.get('range_2')), line_header_light_period)
                                sheet.write_number(row_pos, 7,
                                                        float(sub_line.get('range_3')), line_header_light_period)
                                sheet.write_number(row_pos, 8,
                                                        float(sub_line.get('range_4')), line_header_light_period)
                                sheet.write_number(row_pos, 9,
                                                        float(sub_line.get('range_5')), line_header_light_period)
                                sheet.write_number(row_pos, 10,
                                                        float(sub_line.get('range_6')), line_header_light_period)
                                sheet.write_string(row_pos, 11,
                                                        '', line_header_light_period)

                row_pos += 1
                k = 4
