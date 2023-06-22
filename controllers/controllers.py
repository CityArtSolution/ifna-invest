# -*- coding: utf-8 -*-
# from odoo import http


# class /odoo15/custom/addons/ifna-invest/(http.Controller):
#     @http.route('//odoo15/custom/addons/ifna-invest///odoo15/custom/addons/ifna-invest/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//odoo15/custom/addons/ifna-invest///odoo15/custom/addons/ifna-invest//objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('/odoo15/custom/addons/ifna-invest/.listing', {
#             'root': '//odoo15/custom/addons/ifna-invest///odoo15/custom/addons/ifna-invest/',
#             'objects': http.request.env['/odoo15/custom/addons/ifna-invest/./odoo15/custom/addons/ifna-invest/'].search([]),
#         })

#     @http.route('//odoo15/custom/addons/ifna-invest///odoo15/custom/addons/ifna-invest//objects/<model("/odoo15/custom/addons/ifna-invest/./odoo15/custom/addons/ifna-invest/"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/odoo15/custom/addons/ifna-invest/.object', {
#             'object': obj
#         })
