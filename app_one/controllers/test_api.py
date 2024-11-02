from odoo import http

class TestApi(http.Controller):
    @http.route("/api/test", methods=["GET"], auth="none", csrf=True)
    def test_endpoint(self):
        return "Hello, this is a test endpoint!"
