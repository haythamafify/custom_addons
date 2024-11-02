import json

from odoo import http
from odoo.http import request


class PropertyApi(http.Controller):
    @http.route("/v1/property", methods=["POST"], auth="none", csrf=False)
    def post_property_method(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        res = request.env["property"].sudo.create(vals)
        if res:
            return request.make_json_response({
                "message ": "property has been create successfully"
            }, status=200)
