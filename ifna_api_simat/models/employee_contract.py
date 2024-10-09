# -*- coding: utf-8 -*-

import requests
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime
import json


class IfnaEmployeeContract(models.Model):
    _inherit = 'employee.contract'

    external_id = fields.Integer(index=True)
    tts_days = fields.Integer(string="Period")
    payment_term = fields.Char()
    price_amt = fields.Monetary(string="payments")
    unit = fields.Char()
    property = fields.Char()

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
                timestamp = int(contract['tts_date_dgr'])
                date = datetime.fromtimestamp(timestamp).date()
                partner_name = contract.get('atr_official_name_fo', '')

                if not partner_name:
                    print(f"Skipping contract {contract.get('tts_code')} due to missing name")
                    continue  # Skip this contract if name is not valid

                # Search for an existing partner with this name
                existing_partner = self.env['res.partner'].sudo().search([('name', '=', partner_name)], limit=1)

                if existing_partner:
                    partner_id = existing_partner.id
                else:
                    new_partner = self.env['res.partner'].sudo().create({'name': partner_name, 'is_client': True})
                    partner_id = new_partner.id

                vals = {
                    'external_id': contract.get('tts_id'),
                    'name': contract.get('tts_code'),
                    'date': date,
                    'date_start': start_date,
                    'date_stop': end_date,
                    'tts_days': contract.get('tts_days', False),
                    'payment_term': contract.get('payment_term', False),
                    'price_amt': contract.get('price_amt', False),
                    'unit': contract.get('are_desc_fo', False),
                    'partner_id': partner_id,
                }

                existing_contract = self.sudo().search([('external_id', '=', vals['external_id'])])
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

    # def fetch_data_from_api(self):
    #     url = 'https://dev.simaat.sa/api/odoo/v1/contracts/list'
    #     headers = {'Accept': 'application/json'}
    #
    #     try:
    #         response = requests.get(url, headers=headers)
    #         response.raise_for_status()  # Ensure we notice bad responses
    #     except requests.RequestException as e:
    #         # Handle errors during the request
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'display_notification',
    #             'params': {
    #                 'title': 'Error!',
    #                 'message': f'Failed to fetch contracts: {str(e)}',
    #                 'type': 'danger',
    #                 'sticky': False,
    #             }
    #         }
    #
    #     data = response.json()
    #     contracts = data.get('data', [])
    #
    #     for contract in contracts:
    #         try:
    #             start_date = datetime.fromtimestamp(int(contract['tts_start_date_dgr']))
    #             end_date = datetime.fromtimestamp(int(contract['tts_end_date_dgr']))
    #             timestamp = int(contract['tts_date_dgr'])
    #             date = datetime.fromtimestamp(timestamp).date()
    #             text = contract.get('are_desc_fo', '')
    #             # Split the text into parts
    #             parts = text.split(' ', 1)  # Split into two parts
    #             name = contract.get('atr_official_name_fo')
    #
    #             # Search for an existing partner with this name
    #             existing_partner = self.env['res.partner'].sudo().search([('name', '=', name)], limit=1)
    #
    #             if existing_partner:
    #                 partner_id = existing_partner.id
    #             else:
    #                 # Partner does not exist, create a new one
    #                 new_partner = self.env['res.partner'].sudo().create({'name': name, 'is_client': True})
    #                 partner_id = new_partner.id
    #
    #             vals = {
    #                 'external_id': contract.get('tts_id'),
    #                 'name': contract.get('tts_code'),
    #                 'date': date,
    #                 'date_start': start_date,
    #                 'date_stop': end_date,
    #                 'tts_days': contract.get('tts_days', False),
    #                 'payment_term': contract.get('payment_term', False),
    #                 'price_amt': contract.get('price_amt', False),
    #                 'unit': parts[0] if len(parts) == 2 else False,
    #                 'property': parts[1] if len(parts) == 2 else text,
    #                 'partner_id': partner_id,
    #             }
    #
    #             existing_contract = self.search([('name', '=', vals['name'])])
    #             if existing_contract:
    #                 existing_contract.write(vals)
    #             else:
    #                 self.create(vals)
    #         except (ValueError, KeyError) as e:
    #             print(f"Error processing contract {contract.get('tts_code')}: {e}")
    #
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': 'Contracts Fetched!',
    #             'message': 'Contracts have been successfully fetched and updated.',
    #             'type': 'success',
    #             'sticky': False,
    #         }
    #     }
