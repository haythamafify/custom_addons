import json

from docutils.nodes import status
from odoo import http
from odoo.http import request


class PropertyApi(http.Controller):
    @http.route("/v1/property", methods=["POST"], auth="none", csrf=False)
    def post_property_method(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        # print(args,"args")
        print(vals, "vals")
        if not vals.get("name"):
            return request.make_json_response({
                "message ": "name not found",

            }, status=400)
        try:
            res = request.env["property"].sudo().create(vals)

            if res:
                return request.make_json_response({
                    "message ": "property has been create successfully",
                    "id": res.id,
                    "name": res.name,
                }, status=201)
        except Exception as error:
            return request.make_json_response({
                "message": str(error),
            }, status=400)

    @http.route("/v1/property/json", methods=["POST"], type="json", auth="none", csrf=False)
    def post_property_json(self):
        print("post_property_json")
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        try:
            res = request.env["property"].sudo().create(vals)
            if res:
                return request.make_json_response({
                    "message ": "property has been create successfully from json api",
                }, status=200)
        except  Exception as error:
            return request.make_json_response({
                "message": str(error),
            }, status=400)
