from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Rent(models.Model):
    _inherit = 'sale.order'

