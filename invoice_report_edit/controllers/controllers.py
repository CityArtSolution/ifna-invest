# -*- coding: utf-8 -*-
# from odoo import http


# class AutoFillLines(http.Controller):
#     @http.route('/auto_fill_lines/auto_fill_lines', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/auto_fill_lines/auto_fill_lines/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('auto_fill_lines.listing', {
#             'root': '/auto_fill_lines/auto_fill_lines',
#             'objects': http.request.env['auto_fill_lines.auto_fill_lines'].search([]),
#         })

#     @http.route('/auto_fill_lines/auto_fill_lines/objects/<model("auto_fill_lines.auto_fill_lines"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('auto_fill_lines.object', {
#             'object': obj
#         })
