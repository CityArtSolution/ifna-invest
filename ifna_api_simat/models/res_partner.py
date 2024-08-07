# -*- coding: utf-8 -*-

import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_client = fields.Boolean()

    external_id = fields.Integer('External ID', index=True)

    entity_idtype = fields.Char()

    entity_type = fields.Char()

    entity_number = fields.Char()

    client_tax_code = fields.Char()

    def fetch_and_update_clients(self):
        url = 'https://dev.simaat.sa/api/odoo/v1/clients/list'
        headers = {'Accept': 'application/json'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_json = response.json()

            if 'data' in response_json:
                clients = response_json['data']
                if isinstance(clients, list):
                    for client in clients:
                        self.create_or_update_client(client)

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Clients Fetched!',
                        'message': 'Clients have been successfully fetched and updated.',
                        'type': 'success',
                        'sticky': False,
                    }
                }

        except requests.exceptions.RequestException as e:
            print(f"Error fetching clients: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Error fetching clients: {e}',
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def create_or_update_client(self, client_data):
        partner = self.sudo().search([('external_id', '=', int(client_data['client_id']))], limit=1)

        if partner:
            partner.write({
                'company_type': 'person' if client_data['entity_type'] == "individual" else 'company',
                'entity_idtype': client_data['entity_idtype'],
                'entity_type': client_data['entity_type'],
                'entity_number': client_data['entity_number'],
                'name': client_data['entity_name'],
                'mobile': client_data['contact_mobile'],
                'email': client_data['contact_email'],
                'client_tax_code': client_data['client_tax_code'],
            })
        else:
            self.create({
                'is_client': True,
                'company_type': 'person' if client_data['entity_type'] == "individual" else 'company',
                'external_id': int(client_data['client_id']),
                'entity_idtype': client_data['entity_idtype'],
                'entity_type': client_data['entity_type'],
                'entity_number': client_data['entity_number'],
                'name': client_data['entity_name'],
                'mobile': client_data['contact_mobile'],
                'email': client_data['contact_email'],
                'client_tax_code': client_data['client_tax_code'],
            })





















# import requests
# from odoo import models, fields, api, _
# from odoo.exceptions import UserError
# import json
#
#
# class ResPartner(models.Model):
#     _inherit = 'res.partner'
#
#
#     is_client = fields.Boolean()
#
#     external_id = fields.Char('External ID', index=True)
#
#     entity_idtype = fields.Char()
#
#     entity_type = fields.Char()
#
#     entity_number = fields.Char()
#
#     client_tax_code = fields.Char()
#
#     def fetch_and_update_clients(self):
#         url = 'https://dev.simaat.sa/api/odoo/v1/clients/list'
#         headers = {'Accept': 'application/json'}
#
#         try:
#             response = requests.get(url, headers=headers)
#             response.raise_for_status()
#             response_json = response.json()
#
#             if 'data' in response_json:
#                 clients = response_json['data']
#                 # Ensure clients is a list
#                 if isinstance(clients, list):
#                     for client in clients:
#                         self.create_or_update_client(client)
#
#                 print("clients", clients)
#
#         except requests.exceptions.RequestException as e:
#             print(f"Error fetching clients: {e}")
#
#     def create_or_update_client(self, client_data):
#         partner = self.sudo().search([('external_id', '=', int(client_data['client_id']))], limit=1)
#
#         if partner:
#             partner.write({
#                 'company_type': 'person' if client_data['entity_type'] == "individual" else 'company',
#                 'entity_idtype': client_data['entity_idtype'],
#                 'entity_type': client_data['entity_type'],
#                 'entity_number': client_data['entity_number'],
#                 'name': client_data['entity_name'],
#                 'mobile': client_data['contact_mobile'],
#                 'email': client_data['contact_email'],
#                 'client_tax_code': client_data['client_tax_code'],
#             })
#         else:
#             self.create({
#                 'is_client': True,
#                 'company_type': 'person' if client_data['entity_type'] == "individual" else 'company',
#                 'external_id': int(client_data['client_id']),
#                 'entity_idtype': client_data['entity_idtype'],
#                 'entity_type': client_data['entity_type'],
#                 'entity_number': client_data['entity_number'],
#                 'name': client_data['entity_name'],
#                 'mobile': client_data['contact_mobile'],
#                 'email': client_data['contact_email'],
#                 'client_tax_code': client_data['client_tax_code'],
#             })

