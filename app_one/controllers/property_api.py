from odoo import http
from odoo.http import request
import json

@http.route("/v1/property/json", methods=["POST"], type="http", auth="none", csrf=False)
def post_property_json(self):
    """Create a new property using JSON API."""
    try:
        # قراءة البيانات المرسلة
        args = request.httprequest.data.decode()
        vals = json.loads(args)

        # إنشاء السجل في قاعدة البيانات
        res = request.env["property"].sudo().create(vals)
        if res:
            return request.make_json_response({
                "message": "Property has been created successfully from JSON API",
            }, status=200)
    except json.JSONDecodeError:
        return request.make_json_response({
            "message": "Invalid JSON data",
        }, status=400)
    except Exception as error:
        return request.make_json_response({
            "message": str(error),
        }, status=400)
