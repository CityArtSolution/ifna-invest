# -*- coding: utf-8 -*-
# from odoo import http


# class RentalContractNotification(http.Controller):
#     @http.route('/rental_contract_notification/rental_contract_notification', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rental_contract_notification/rental_contract_notification/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rental_contract_notification.listing', {
#             'root': '/rental_contract_notification/rental_contract_notification',
#             'objects': http.request.env['rental_contract_notification.rental_contract_notification'].search([]),
#         })

#     @http.route('/rental_contract_notification/rental_contract_notification/objects/<model("rental_contract_notification.rental_contract_notification"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rental_contract_notification.object', {
#             'object': obj
#         })
