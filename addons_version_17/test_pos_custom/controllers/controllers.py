# -*- coding: utf-8 -*-
# from odoo import http


# class TestPosCustom(http.Controller):
#     @http.route('/test_pos_custom/test_pos_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_pos_custom/test_pos_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_pos_custom.listing', {
#             'root': '/test_pos_custom/test_pos_custom',
#             'objects': http.request.env['test_pos_custom.test_pos_custom'].search([]),
#         })

#     @http.route('/test_pos_custom/test_pos_custom/objects/<model("test_pos_custom.test_pos_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_pos_custom.object', {
#             'object': obj
#         })

