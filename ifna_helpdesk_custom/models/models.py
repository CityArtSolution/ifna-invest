from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class HelpDeskCustom(models.Model):
    _inherit = 'helpdesk.ticket'


class HelpDeskCustomType(models.Model):
    _inherit = 'helpdesk.ticket.type'

    helpdesk_teams_ids = fields.Many2many(comodel_name="helpdesk.team", relation="rel_team_type", string="Helpdesk Team", )
