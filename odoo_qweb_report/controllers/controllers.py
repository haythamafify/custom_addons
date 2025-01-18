# -*- coding: utf-8 -*-
# from odoo import http


# class OdooQwebReport(http.Controller):
#     @http.route('/odoo_qweb_report/odoo_qweb_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_qweb_report/odoo_qweb_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_qweb_report.listing', {
#             'root': '/odoo_qweb_report/odoo_qweb_report',
#             'objects': http.request.env['odoo_qweb_report.odoo_qweb_report'].search([]),
#         })

#     @http.route('/odoo_qweb_report/odoo_qweb_report/objects/<model("odoo_qweb_report.odoo_qweb_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_qweb_report.object', {
#             'object': obj
#         })

