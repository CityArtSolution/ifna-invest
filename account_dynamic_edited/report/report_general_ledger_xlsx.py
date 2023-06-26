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


class InsGeneralLedgerXlsx(models.AbstractModel):
    _name = 'report.account_dynamic_edited.ins_general_ledger_xlsx'
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

        # def get_xlsx_report(self, data, response):

            # Initialize
            #############################################################
            # output = io.BytesIO()
            # workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('General Ledger')
        sheet.set_zoom(95)
        sheet_2 = workbook.add_worksheet('Filters')
        sheet_2.protect()

        # Get record and data
        # record = self.env['report.ins.general.ledger'].browse(data.get('id', [])) or False
        filter, account_lines = record.get_report_datas()

        # Formats
        ############################################################
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 3, 18)
        sheet.set_column(4, 4, 30)
        sheet.set_column(5, 5, 13)
        sheet.set_column(6, 6, 13)
        sheet.set_column(7, 7, 13)

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

        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
            'border': False
        })
        format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font': 'Arial',
            'align': 'center',
            # 'border': True
        })
        content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'border': True,
            'text_wrap': True,
        })
        content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'border': True,
            'align': 'center',
            'font': 'Arial',
        })
        line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'bottom': True,
        })
        line_header_left = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'top': True,
            'font': 'Arial',
            'bottom': True,
        })
        line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            # 'top': True,
            # 'bottom': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top'
        })
        line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            # 'top': True,
            # 'bottom': True,
            'font': 'Arial',
            'align': 'center',
        })
        line_header_light_initial = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'bottom': True,
            'text_wrap': True,
            'valign': 'top'
        })
        line_header_light_initial_bold = workbook.add_format({
            'bold': True,
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top'
        })
        line_header_light_ending = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top'
        })
        line_header_light_ending_bold = workbook.add_format({
            'bold': True,
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'text_wrap': True,
            'valign': 'top'
        })

        lang = self.env.user.lang
        lang_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        currency_id = self.env.user.company_id.currency_id
        line_header.num_format = currency_id.excel_format
        line_header_light.num_format = currency_id.excel_format
        line_header_light_initial.num_format = currency_id.excel_format
        line_header_light_ending.num_format = currency_id.excel_format
        line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        content_header_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

        # Write data
        ################################################################
        row_pos_2 = 0
        row_pos = 0
        sheet.merge_range(0, 0, 0, 8, 'General Ledger' + ' - ' + data['company_id'][1], format_title)

        # Write filters
        sheet_2.write(row_pos_2, 0, _('Date from'), format_header)
        datestring = fields.Date.from_string(str(filter['date_from'])).strftime(lang_id.date_format)
        sheet_2.write(row_pos_2, 1, datestring or '', content_header_date)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Date to'), format_header)
        datestring = fields.Date.from_string(str(filter['date_to'])).strftime(lang_id.date_format)
        sheet_2.write(row_pos_2, 1, datestring or '', content_header_date)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Target moves'), format_header)
        sheet_2.write(row_pos_2, 1, filter['target_moves'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Display accounts'), format_header)
        sheet_2.write(row_pos_2, 1, filter['display_accounts'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Sort by'), format_header)
        sheet_2.write(row_pos_2, 1, filter['sort_accounts_by'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Initial Balance'), format_header)
        sheet_2.write(row_pos_2, 1, filter['initial_balance'], content_header)
        row_pos_2 += 1
        row_pos_2 += 2
        sheet_2.write(row_pos_2, 0, _('Journals'), format_header)
        j_list = ', '.join([lt or '' for lt in filter.get('journals')])
        sheet_2.write(row_pos_2, 1, j_list, content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Partners'), format_header)
        p_list = ', '.join([lt or '' for lt in filter.get('partners')])
        sheet_2.write(row_pos_2, 1, p_list, content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Accounts'), format_header)
        a_list = ', '.join([lt or '' for lt in filter.get('accounts')])
        sheet_2.write(row_pos_2, 1, a_list, content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Account Tags'), format_header)
        a_list = ', '.join([lt or '' for lt in filter.get('account_tags')])
        sheet_2.write(row_pos_2, 1, a_list, content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Analytic Accounts'), format_header)
        a_list = ', '.join([lt or '' for lt in filter.get('analytics')])
        sheet_2.write(row_pos_2, 1, a_list, content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Analytic Tags'), format_header)
        a_list = ', '.join([lt or '' for lt in filter.get('analytic_tags')])
        sheet_2.write(row_pos_2, 1, a_list, content_header)

        # Write Ledger details
        row_pos += 3
        if filter.get('include_details', False):
            sheet.write_string(row_pos, 0, _('Date'), format_header)
            sheet.write_string(row_pos, 1, _('JRNL'), format_header)
            sheet.write_string(row_pos, 2, _('Partner'), format_header)
            # self.sheet.write_string(row_pos, 3, _('Ref'),self.format_header)
            sheet.write_string(row_pos, 3, _('Move'), format_header)
            sheet.write_string(row_pos, 4, _('Entry Label'), format_header)
            sheet.write_string(row_pos, 5, _('Debit'), format_header)
            sheet.write_string(row_pos, 6, _('Credit'), format_header)
            sheet.write_string(row_pos, 7, _('Balance'), format_header)
        else:
            sheet.merge_range(row_pos, 0, row_pos, 1, _('Code'), format_header)
            sheet.merge_range(row_pos, 2, row_pos, 4, _('Account'), format_header)
            sheet.write_string(row_pos, 5, _('Debit'), format_header)
            sheet.write_string(row_pos, 6, _('Credit'), format_header)
            sheet.write_string(row_pos, 7, _('Balance'), format_header)

        if account_lines:
            for line in account_lines:
                row_pos += 1
                if filter.get('include_details', False):
                    account_id = account_lines[line].get('id')
                    count, offset, sub_lines = record.build_detailed_move_lines(offset=0, account=account_id,
                                                                                fetch_range=1000000)
                    sheet.merge_range(row_pos, 0, row_pos, 4,
                                      '            ' + account_lines[line].get('code') + ' - ' + account_lines[
                                          line].get('name'), line_header_left)
                    sheet.write(row_pos, 5, account_lines[line].get('debit'), line_header)
                    sheet.write(row_pos, 6, account_lines[line].get('credit'), line_header)
                    sheet.write(row_pos, 7, account_lines[line].get('balance'), line_header)

                    for sub_line in sub_lines:
                        if sub_line.get('move_name') == 'Initial Balance':
                            row_pos += 1
                            sheet.write(row_pos, 4, sub_line.get('move_name'), line_header_light_initial_bold)
                            sheet.write(row_pos, 5, float(sub_line.get('debit')), line_header_light_initial)
                            sheet.write(row_pos, 6, float(sub_line.get('credit')), line_header_light_initial)
                            sheet.write(row_pos, 7, float(sub_line.get('balance')), line_header_light_initial)
                        elif sub_line.get('move_name') not in ['Initial Balance', 'Ending Balance']:
                            row_pos += 1
                            datestring = fields.Date.from_string(str(sub_line.get('ldate'))).strftime(
                                lang_id.date_format)
                            sheet.write(row_pos, 0, datestring, line_header_light_date)
                            sheet.write(row_pos, 1, sub_line.get('lcode'), line_header_light)
                            sheet.write(row_pos, 2, sub_line.get('partner_name') or '', line_header_light)
                            # sheet.write_string(row_pos, 3, sub_line.get('lref') or '', line_header_light)
                            sheet.write(row_pos, 3, sub_line.get('move_name'), line_header_light)
                            sheet.write(row_pos, 4, sub_line.get('lname') or '', line_header_light)
                            sheet.write(row_pos, 5, float(sub_line.get('debit')), line_header_light)
                            sheet.write(row_pos, 6, float(sub_line.get('credit')), line_header_light)
                            sheet.write(row_pos, 7, float(sub_line.get('balance')), line_header_light)
                        else:  # Ending Balance
                            row_pos += 1
                            sheet.write(row_pos, 4, sub_line.get('move_name'), line_header_light_ending_bold)
                            sheet.write(row_pos, 5, float(sub_line.get('debit')),
                                        line_header_light_ending)
                            sheet.write(row_pos, 6, float(sub_line.get('credit')),
                                        line_header_light_ending)
                            sheet.write(row_pos, 7, float(sub_line.get('balance')),
                                        line_header_light_ending)

        # Close and return
        #################################################################
        workbook.close()
    #
    # def generate_xlsx_report(self, workbook, data, record):
    #     print("///////////////////////////////report")
    #     """ Add cell formats to current workbook.
    #     Available formats:
    #      * format_title
    #      * format_header
    #     """
    #     format_title = workbook.add_format({
    #         'bold': True,
    #         'font_size': 10,
    #         'font': 'Arial',
    #         'align': 'center',
    #         # 'border': True
    #     })
    #     content_header = workbook.add_format({
    #         'bold': False,
    #         'font_size': 10,
    #         'align': 'center',
    #         'font': 'Arial',
    #         'border': True,
    #         'text_wrap': True,
    #     })
    #     content_header_date = workbook.add_format({
    #         'bold': False,
    #         'font_size': 10,
    #         'border': True,
    #         'align': 'center',
    #         'font': 'Arial',
    #     })
    #     line_header = workbook.add_format({
    #         'bold': True,
    #         'font_size': 10,
    #         'align': 'center',
    #         'top': True,
    #         'font': 'Arial',
    #         'bottom': True,
    #     })
    #     line_header_left = workbook.add_format({
    #         'bold': True,
    #         'font_size': 10,
    #         'align': 'left',
    #         'top': True,
    #         'font': 'Arial',
    #         'bottom': True,
    #     })
    #     line_header_light = workbook.add_format({
    #         'bold': False,
    #         'font_size': 10,
    #         'align': 'center',
    #         # 'top': True,
    #         # 'bottom': True,
    #         'font': 'Arial',
    #         'text_wrap': True,
    #         'valign': 'top'
    #     })
    #     line_header_light_date = workbook.add_format({
    #         'bold': False,
    #         'font_size': 10,
    #         # 'top': True,
    #         # 'bottom': True,
    #         'font': 'Arial',
    #         'align': 'center',
    #     })
    #     line_header_light_initial = workbook.add_format({
    #         'italic': True,
    #         'font_size': 10,
    #         'align': 'center',
    #         'font': 'Arial',
    #         'bottom': True,
    #         'text_wrap': True,
    #         'valign': 'top'
    #     })
    #     line_header_light_ending = workbook.add_format({
    #         'italic': True,
    #         'font_size': 10,
    #         'align': 'center',
    #         'top': True,
    #         'font': 'Arial',
    #         'text_wrap': True,
    #         'valign': 'top'
    #     })
    #
    #     record = record  # Wizard object
    #     sheet = workbook.add_worksheet('General Ledger')
    #     sheet_2 = workbook.add_worksheet('Filters')
    #     sheet.set_column(0, 0, 12)
    #     sheet.set_column(1, 1, 12)
    #     sheet.set_column(2, 2, 30)
    #     sheet.set_column(3, 3, 18)
    #     sheet.set_column(4, 4, 30)
    #     sheet.set_column(5, 5, 10)
    #     sheet.set_column(6, 6, 10)
    #     sheet.set_column(7, 7, 10)
    #
    #     sheet_2.set_column(0, 0, 35)
    #     sheet_2.set_column(1, 1, 25)
    #     sheet_2.set_column(2, 2, 25)
    #     sheet_2.set_column(3, 3, 25)
    #     sheet_2.set_column(4, 4, 25)
    #     sheet_2.set_column(5, 5, 25)
    #     sheet_2.set_column(6, 6, 25)
    #
    #     sheet.freeze_panes(4, 0)
    #
    #     sheet.screen_gridlines = False
    #     sheet_2.screen_gridlines = False
    #     sheet_2.protect()
    #
    #     # For Formating purpose
    #     lang = self.env.user.lang
    #     currency_id = self.env.user.company_id.currency_id
    #     lang_id = self.env['res.lang'].search([('code', '=', lang)])[0]
    #     line_header.num_format = currency_id.excel_format
    #     line_header_light.num_format = currency_id.excel_format
    #     line_header_light_initial.num_format = currency_id.excel_format
    #     line_header_light_ending.num_format = currency_id.excel_format
    #
    #     line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
    #     content_header_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
    #
    #
    #     if record:
    #         data = record.read()
    #         sheet.merge_range(0, 0, 0, 8, 'General Ledger' + ' - ' + data[0]['company_id'][1], format_title)
    #         dateformat = self.env.user.lang
    #         filter, account_lines = record.get_report_datas()
    #         # Filter section
    #         row_pos_2 = 0
    #         row_pos_2 += 2
    #         if filter:
    #             # Date from
    #             sheet_2.write_string(row_pos_2, 0, _('Date from'),
    #                                  format_title)
    #             sheet_2.write_datetime(row_pos_2, 1, self.convert_to_date(str(filter['date_from']) or ''),
    #                                    content_header_date)
    #
    #             row_pos_2 += 1
    #             sheet_2.write_string(row_pos_2, 0, _('Date to'),
    #                                  format_title)
    #             sheet_2.write_datetime(row_pos_2, 1, self.convert_to_date(str(filter['date_to']) or ''),
    #                                    content_header_date)
    #             row_pos_2 += 1
    #             sheet_2.write_string(row_pos_2, 0, _('Target moves'),
    #                                  format_title)
    #             sheet_2.write_string(row_pos_2, 1, filter['target_moves'],
    #                                  content_header)
    #             row_pos_2 += 1
    #             sheet_2.write_string(row_pos_2, 0, _('Display accounts'),
    #                                  format_title)
    #             sheet_2.write_string(row_pos_2, 1, filter['display_accounts'],
    #                                  content_header)
    #             row_pos_2 += 1
    #             sheet_2.write_string(row_pos_2, 0, _('Sort by'),
    #                                  format_title)
    #             sheet_2.write_string(row_pos_2, 1, filter['sort_accounts_by'],
    #                                  content_header)
    #             row_pos_2 += 1
    #             sheet_2.write_string(row_pos_2, 0, _('Initial Balance'),
    #                                  format_title)
    #             sheet_2.write_string(row_pos_2, 1, filter['initial_balance'],
    #                                  content_header)
    #             row_pos_2 += 1
    #
    #             # Journals
    #             row_pos_2 += 2
    #             sheet_2.write_string(row_pos_2, 0, _('Journals'),
    #                                  format_title)
    #             j_list = ', '.join([lt or '' for lt in filter.get('journals')])
    #             sheet_2.write_string(row_pos_2, 1, j_list,
    #                                  content_header)
    #
    #             # Partners
    #             row_pos_2 += 1
    #             sheet_2.write_string(row_pos_2, 0, _('Partners'),
    #                                  format_title)
    #             p_list = ', '.join([lt or '' for lt in filter.get('partners')])
    #             sheet_2.write_string(row_pos_2, 1, p_list,
    #                                  content_header)
    #
    #             # Accounts
    #             row_pos_2 += 1
    #             sheet_2.write_string(row_pos_2, 0, _('Accounts'),
    #                                  format_title)
    #             a_list = ', '.join([lt or '' for lt in filter.get('accounts')])
    #             sheet_2.write_string(row_pos_2, 1, a_list,
    #                                  content_header)
    #
    #             # Account Tags
    #             row_pos_2 += 1
    #             sheet_2.write_string(row_pos_2, 0, _('Account Tags'),
    #                                  format_title)
    #             a_list = ', '.join([lt or '' for lt in filter.get('account_tags')])
    #             sheet_2.write_string(row_pos_2, 1, a_list,
    #                                  content_header)
    #
    #             # Analytic Accounts
    #             row_pos_2 += 1
    #             sheet_2.write_string(row_pos_2, 0, _('Analytic Accounts'),
    #                                  format_title)
    #             a_list = ', '.join([lt or '' for lt in filter.get('analytics')])
    #             sheet_2.write_string(row_pos_2, 1, a_list,
    #                                  content_header)
    #
    #             # Analytic Tags
    #             row_pos_2 += 1
    #             sheet_2.write_string(row_pos_2, 0, _('Analytic Tags'),
    #                                  format_title)
    #             a_list = ', '.join([lt or '' for lt in filter.get('analytic_tags')])
    #             sheet_2.write_string(row_pos_2, 1, a_list,
    #                                  content_header)
    #         # self.prepare_report_filters(filters)
    #         # Content section
    #         row_pos = 0
    #         row_pos += 3
    #
    #         if filter.get('include_details', False):
    #             sheet.write_string(row_pos, 0, _('Date'),
    #                                     format_title)
    #             sheet.write_string(row_pos, 1, _('JRNL'),
    #                                     format_title)
    #             sheet.write_string(row_pos, 2, _('Partner'),
    #                                     format_title)
    #             # sheet.write_string(row_pos, 3, _('Ref'),
    #             #                         format_title)
    #             sheet.write_string(row_pos, 3, _('Move'),
    #                                     format_title)
    #             sheet.write_string(row_pos, 4, _('Entry Label'),
    #                                     format_title)
    #             sheet.write_string(row_pos, 5, _('Debit'),
    #                                     format_title)
    #             sheet.write_string(row_pos, 6, _('Credit'),
    #                                     format_title)
    #             sheet.write_string(row_pos, 7, _('Balance'),
    #                                     format_title)
    #         else:
    #             sheet.merge_range(row_pos, 0, row_pos, 1, _('Code'), format_title)
    #             sheet.merge_range(row_pos, 2, row_pos, 4, _('Account'), format_title)
    #             sheet.write_string(row_pos, 5, _('Debit'),
    #                                     format_title)
    #             sheet.write_string(row_pos, 6, _('Credit'),
    #                                     format_title)
    #             sheet.write_string(row_pos, 7, _('Balance'),
    #                                     format_title)
    #
    #         if account_lines:
    #             for line in account_lines:
    #                 row_pos += 1
    #                 sheet.merge_range(row_pos, 0, row_pos, 4,
    #                                        '            ' + account_lines[line].get('code') + ' - ' + account_lines[line].get(
    #                                            'name'), line_header_left)
    #                 sheet.write_number(row_pos, 5, float(account_lines[line].get('debit')), line_header)
    #                 sheet.write_number(row_pos, 6, float(account_lines[line].get('credit')), line_header)
    #                 sheet.write_number(row_pos, 7, float(account_lines[line].get('balance')), line_header)
    #
    #                 if filter.get('include_details', False):
    #
    #                     count, offset, sub_lines = record.build_detailed_move_lines(offset=0, account=line,
    #                                                                                      fetch_range=1000000)
    #
    #                     for sub_line in sub_lines:
    #                         if sub_line.get('move_name') == 'Initial Balance':
    #                             row_pos += 1
    #                             sheet.write_string(row_pos, 4, sub_line.get('move_name'),
    #                                                     line_header_light_initial)
    #                             sheet.write_number(row_pos, 5, float(account_lines[line].get('debit')),
    #                                                     line_header_light_initial)
    #                             sheet.write_number(row_pos, 6, float(account_lines[line].get('credit')),
    #                                                     line_header_light_initial)
    #                             sheet.write_number(row_pos, 7, float(account_lines[line].get('balance')),
    #                                                     line_header_light_initial)
    #                         elif sub_line.get('move_name') not in ['Initial Balance', 'Ending Balance']:
    #                             row_pos += 1
    #                             sheet.write_datetime(row_pos, 0, self.convert_to_date(sub_line.get('ldate')),
    #                                                       line_header_light_date)
    #                             sheet.write_string(row_pos, 1, sub_line.get('lcode'),
    #                                                     line_header_light)
    #                             sheet.write_string(row_pos, 2, sub_line.get('partner_name') or '',
    #                                                     line_header_light)
    #                             # sheet.write_string(row_pos, 3, sub_line.get('lref') or '',
    #                             #                         line_header_light)
    #                             sheet.write_string(row_pos, 3, sub_line.get('move_name'),
    #                                                     line_header_light)
    #                             sheet.write_string(row_pos, 4, sub_line.get('lname') or '',
    #                                                     line_header_light)
    #                             sheet.write_number(row_pos, 5,
    #                                                     float(sub_line.get('debit')), line_header_light)
    #                             sheet.write_number(row_pos, 6,
    #                                                     float(sub_line.get('credit')), line_header_light)
    #                             sheet.write_number(row_pos, 7,
    #                                                     float(sub_line.get('balance')), line_header_light)
    #                         else:  # Ending Balance
    #                             row_pos += 1
    #                             sheet.write_string(row_pos, 4, sub_line.get('move_name'),
    #                                                     line_header_light_ending)
    #                             sheet.write_number(row_pos, 5, float(account_lines[line].get('debit')),
    #                                                     line_header_light_ending)
    #                             sheet.write_number(row_pos, 6, float(account_lines[line].get('credit')),
    #                                                     line_header_light_ending)
    #                             sheet.write_number(row_pos, 7, float(account_lines[line].get('balance')),
    #                                                     line_header_light_ending)
    #
