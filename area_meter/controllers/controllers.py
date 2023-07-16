# -*- coding: utf-8 -*-
# from odoo import http


# class AreaMeter(http.Controller):
#     @http.route('/area_meter/area_meter', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/area_meter/area_meter/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('area_meter.listing', {
#             'root': '/area_meter/area_meter',
#             'objects': http.request.env['area_meter.area_meter'].search([]),
#         })

#     @http.route('/area_meter/area_meter/objects/<model("area_meter.area_meter"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('area_meter.object', {
#             'object': obj
#         })
