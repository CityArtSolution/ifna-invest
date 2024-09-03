# -*- coding: utf-8 -*-
# from odoo import http


# class LegalAffairsManagement(http.Controller):
#     @http.route('/legal_affairs_management/legal_affairs_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/legal_affairs_management/legal_affairs_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('legal_affairs_management.listing', {
#             'root': '/legal_affairs_management/legal_affairs_management',
#             'objects': http.request.env['legal_affairs_management.legal_affairs_management'].search([]),
#         })

#     @http.route('/legal_affairs_management/legal_affairs_management/objects/<model("legal_affairs_management.legal_affairs_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('legal_affairs_management.object', {
#             'object': obj
#         })
