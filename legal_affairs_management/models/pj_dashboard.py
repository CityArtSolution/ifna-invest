# -*- coding: utf-8 -*-

import calendar
import random
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, api


class PosDashboard(models.Model):
    _inherit = 'legal.case'

    @api.model
    def get_tiles_data(self):
        """
        Summery:
            when the page is loaded get the data from different models and transfer to the js file.
            return a dictionary variable.
        return:
            type:It is a dictionary variable. This dictionary contain data that affecting the dashboard view.
        """
        all_consultation = self.env['external.legal.consultation'].search([])
        all_auth_agen = self.env['legal.authorization.agency'].search([])
        all_decision = self.env['legal.board.decision'].search([])
        all_opened_cases = self.env['legal.case'].search([('case_status', '=', 'open')])
        all_requests = self.env['legal.execution.request'].search([])
        all_paid_requests = self.env['legal.execution.request'].search([('state', '=', 'paid')])
        all_unpaid_requests = self.env['legal.execution.request'].search([('state', '=', 'not_paid')])
        company_currency = self.env.company.currency_id.symbol
        all_clients = self.env['res.partner'].search([('is_legal_defendant', '=', True)])

        return {
            'total_consultations': len(all_consultation),
            'total_auths_agens': len(all_auth_agen),
            'total_decisions': len(all_decision),
            'total_opened_cases': len(all_opened_cases),
            'total_requests': len(all_requests),
            'total_paids': f"{sum(paid.execution_amount for paid in all_paid_requests):,.2f} {company_currency}",
            'total_unpaids': f"{sum(paid.execution_amount for paid in all_unpaid_requests):,.2f} {company_currency}",
            'total_clients': len(all_clients),
        }

    @api.model
    def get_legal_case_data(self):
        """
        Fetches legal case data using Odoo ORM and returns it in a dictionary.
        Returns:
            dict: A dictionary containing legal case data.
        """
        cases = self.search([])  # Adjust the domain if needed
        case_data = []
        for case in cases:
            case_data.append({
                'id': case.id,
                'name': case.name,
                'court_name': case.court_id.name if case.court_id else '',
                'lawyer_name': case.lawyer_id.name if case.lawyer_id else '',
                'plaintiff_name': case.plaintiff_id.name if case.plaintiff_id else '',
                'defendant_name': case.partner_id.name if case.partner_id else '',
                'trials': case.legal_trail_count,
                'claim_amount': str(case.claim_amount) + ' ' + case.currency_id.symbol,
                'case_status': case.case_status,
            })
        return {
            'case_data': case_data
        }

