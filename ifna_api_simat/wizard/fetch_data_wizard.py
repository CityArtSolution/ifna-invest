# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class FetchDataWizard(models.TransientModel):
    _name = 'fetch.data.wizard'
    _description = 'Wizard to Fetch and Update Data'

    result_message = fields.Text(
        default=lambda self: _("Easily fetch and update client or contract information manually.")
    )

    def fetch_and_update_clients(self):
        self.env['res.partner'].fetch_and_update_clients()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def fetch_data_from_api(self):
        self.env['employee.contract'].fetch_data_from_api()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def cancel_action(self):
        return {'type': 'ir.actions.act_window_close'}
