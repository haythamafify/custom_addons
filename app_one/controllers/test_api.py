from odoo import http


class Test(http.Controller):
    @http.route()
    def test_endpoint(self):
        print("inside test_endpoint")
        
