# -*- coding: utf-8 -*-

import requests
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime
import json


class EmployeeContract(models.Model):
    _name = 'employee.contract'
    _description = "IFNA Employee Contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    stage_id = fields.Many2one('employee.contract.stage', tracking=True, default=lambda self: self._default_stage())
    name = fields.Char(tracking=True)
    image_1920 = fields.Binary(tracking=True)
    partner_id = fields.Many2one('res.partner', string="Client", tracking=True)
    phone = fields.Char(tracking=True)
    email = fields.Char(tracking=True)
    date = fields.Date(tracking=True)
    date_start = fields.Datetime(tracking=True)
    date_stop = fields.Datetime(tracking=True)
    user_id = fields.Many2one('res.users', string="Responsible", tracking=True)
    amount = fields.Monetary(string="Value", tracking=True)
    tag_ids = fields.Many2many('employee.contract.tag', string="Tags", tracking=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company.id,
                                 tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.company.currency_id.id, tracking=True)
    description = fields.Html(string="Description", tracking=True)
    employee_contract_line_ids = fields.One2many('employee.contract.line', 'contract_id')
    color = fields.Integer(string="Color")
    kanban_state = fields.Selection(
        [('normal', 'Normal'), ('done', 'Done'), ('blocked', 'Blocked')],
        string="Kanban State",
        default='normal'
    )

    @api.model
    def _default_stage(self):
        return self.env['employee.contract.stage'].search([('name', '=', 'New')], limit=1).id

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start and self.date_stop:
            if self.date_stop < self.date_start:
                self.date_stop = False
        if self.date_start:
            self.date_stop = self.date_start + timedelta(days=1)

    # @api.constrains('date_stop')
    # def _check_date_stop(self):
    #     for record in self:
    #         if record.date_stop and record.date_start:
    #             if record.date_stop < record.date_start:
    #                 raise ValidationError("The end date must be greater than or equal to the start date.")

    def fetch_data_from_api(self):
        url = 'https://dev.simaat.sa/api/odoo/v1/contracts/list'
        headers = {'Accept': 'application/json'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Ensure we notice bad responses
        except requests.RequestException as e:
            # Handle errors during the request
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error!',
                    'message': f'Failed to fetch contracts: {str(e)}',
                    'type': 'danger',
                    'sticky': False,
                }
            }

        data = response.json()
        contracts = data.get('data', [])

        for contract in contracts:
            try:
                start_date = datetime.fromtimestamp(int(contract['tts_start_date_dgr']))
                end_date = datetime.fromtimestamp(int(contract['tts_end_date_dgr']))

                vals = {
                    'external_id': contract.get('tts_id'),
                    'name': contract.get('tts_code'),
                    'date_start': start_date,
                    'date_stop': end_date,
                    'duration': contract.get('tts_duration', ''),
                }

                existing_contract = self.search([('name', '=', vals['name'])])
                if existing_contract:
                    existing_contract.write(vals)
                else:
                    self.create(vals)
            except (ValueError, KeyError) as e:
                print(f"Error processing contract {contract.get('tts_code')}: {e}")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Contracts Fetched!',
                'message': 'Contracts have been successfully fetched and updated.',
                'type': 'success',
                'sticky': False,
            }
        }


class EmployeeContractLine(models.Model):
    _name = 'employee.contract.line'
    _description = "IFNA Employee Contract Line"

    active = fields.Boolean(default=True)
    name = fields.Char()
    sequence = fields.Integer()
    contract_id = fields.Many2one('employee.contract')
