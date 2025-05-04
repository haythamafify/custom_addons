# -*- coding: utf-8 -*-
# from odoo import http


# class HospitlaMangementSystem(http.Controller):
#     @http.route('/hospitla_mangement_system/hospitla_mangement_system', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hospitla_mangement_system/hospitla_mangement_system/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hospitla_mangement_system.listing', {
#             'root': '/hospitla_mangement_system/hospitla_mangement_system',
#             'objects': http.request.env['hospitla_mangement_system.hospitla_mangement_system'].search([]),
#         })

#     @http.route('/hospitla_mangement_system/hospitla_mangement_system/objects/<model("hospitla_mangement_system.hospitla_mangement_system"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hospitla_mangement_system.object', {
#             'object': obj
#         })

