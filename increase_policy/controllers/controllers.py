# -*- coding: utf-8 -*-
# from odoo import http


# class IncreasePolicy(http.Controller):
#     @http.route('/increase_policy/increase_policy', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/increase_policy/increase_policy/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('increase_policy.listing', {
#             'root': '/increase_policy/increase_policy',
#             'objects': http.request.env['increase_policy.increase_policy'].search([]),
#         })

#     @http.route('/increase_policy/increase_policy/objects/<model("increase_policy.increase_policy"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('increase_policy.object', {
#             'object': obj
#         })
