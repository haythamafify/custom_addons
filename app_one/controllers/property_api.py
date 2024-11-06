import json
from logging import exception

from docutils.nodes import status
from odoo import http
from odoo.http import request, route
from urllib.parse import parse_qs


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

    class PropertyController(http.Controller):

        @http.route("/v1/property/<int:property_id>", methods=["PUT"], type="http", auth="none", csrf=False)
        def update_property(self, property_id):
            property_record = request.env['property'].sudo().search([("id", "=", property_id)])

            if not property_record:
                return request.make_json_response({"message": "Property not found"}, 404)

            try:
                args = request.httprequest.data.decode()
                vals = json.loads(args)
                property_record.write(vals)

                return request.make_json_response({
                    "message": "Property has been updated successfully",
                    "id": property_record.id,
                    "name": property_record.name,
                }, status=200)  # Note the explicit status parameter

            except json.JSONDecodeError:
                return request.make_json_response({"message": "Invalid JSON data"}, 400)

        @http.route("/v1/property/<int:property_id>", methods=["GET"], type="http", auth="none", csrf=False)
        def get_property(self, property_id):
            try:
                property_record = request.env['property'].sudo().search([("id", "=", property_id)])
                if property_record:
                    return request.make_json_response(
                        {
                            "name": property_record.name,
                            "description": property_record.description,
                            "postcode": property_record.postcode,
                            "state": property_record.state,
                        }, status=200)

                else:
                    return request.make_json_response({"message": "Property ID does not exist"}, status=400)

            except Exception as error:
                return request.make_json_response({"message": error}, status=400)

        @http.route("/v1/property/<int:property_id>", methods=["DELETE"], type="http", auth="none", csrf=False)
        def delete_property(self, property_id):
            try:
                property_record = request.env['property'].sudo().search([("id", "=", property_id)])
                if property_record:
                    property_record.unlink()
                    return request.make_json_response(
                        {
                            "message": "property has been removed successfully"
                        }, status=200)

                else:
                    return request.make_json_response({"message": "Property ID does not exist"}, status=400)

            except Exception as error:
                return request.make_json_response({"message": error}, status=400)

        @http.route("/v1/properties", methods=["GET"], type="http", auth="none", csrf=False)
        def get_property_list(self):
            try:

                params = parse_qs(request.httprequest.query_string.decode('utf-8'))
                property_domain = []
                print(params)
                print("before", property_domain)

                if params.get('state'):
                    property_domain += [('state', '=', params.get('state')[0])]
                print("after", property_domain)

                property_records = request.env['property'].sudo().search(property_domain)
                print("property_records", property_records)

                if not property_records:
                    return request.make_json_response({"message": "Property IDs do not exist"}, status=400)

                return request.make_json_response(
                    [{
                        "name": property_record.name,
                        "description": property_record.description,
                        "postcode": property_record.postcode,
                        "state": property_record.state,
                    } for property_record in property_records], status=200)

            except Exception as error:

                return request.make_json_response({"message": str(error)}, status=400)
