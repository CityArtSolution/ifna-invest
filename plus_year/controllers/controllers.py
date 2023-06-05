# -*- coding: utf-8 -*-
# from odoo import http


# class PlusYear(http.Controller):
#     @http.route('/plus_year/plus_year', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/plus_year/plus_year/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('plus_year.listing', {
#             'root': '/plus_year/plus_year',
#             'objects': http.request.env['plus_year.plus_year'].search([]),
#         })

#     @http.route('/plus_year/plus_year/objects/<model("plus_year.plus_year"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('plus_year.object', {
#             'object': obj
#         })
