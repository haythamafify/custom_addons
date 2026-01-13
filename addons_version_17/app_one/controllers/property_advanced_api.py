import json
import math
from urllib.parse import parse_qs

from odoo import http
from odoo.http import request, Response


# دوال الاستجابة العامة
def valid_response(data, pagination_info, status=200, message="Success"):
    """إرجاع استجابة JSON ناجحة."""
    response_body = {
        'status': status,
        'message': message,
        'data': data,
    }
    if pagination_info:
        response_body['pagination_info'] = pagination_info
    return request.make_json_response(response_body, status=status)


def invalid_response(error, status=400, message="Error"):
    """إرجاع استجابة JSON في حالة وجود خطأ."""
    response_body = {
        'status': status,
        'message': message,
        'error': error,
    }
    return request.make_json_response(response_body, status=status)


# الفئة الرئيسية للتحكم في العقارات
class PropertyController(http.Controller):

    # إنشاء عقار جديد
    @http.route("/v2/property", methods=["POST"], type="http", auth="none", csrf=False)
    def create_property(self):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)

            # التحقق من وجود الحقول المطلوبة
            if not vals.get("name"):
                return invalid_response("Field 'name' is required", status=400)

            # إنشاء السجل
            res = request.env["property"].sudo().create(vals)
            if res:
                return valid_response({
                    "id": res.id,
                    "name": res.name,
                }, status=201, message="Property created successfully")
        except json.JSONDecodeError:
            return invalid_response("Invalid JSON data", status=400)
        except Exception as error:
            return invalid_response(str(error), status=500)

    #     http://127.0.0.1:8069/v3/property

    # استرجاع بيانات عقار بناءً على ID

    @http.route("/v2/property/<int:property_id>", methods=["GET"], type="http", auth="none", csrf=False)
    def get_property(self, property_id):
        try:
            property_record = request.env['property'].sudo().search([("id", "=", property_id)], limit=1)
            if property_record:
                return valid_response({
                    "name": property_record.name,
                    "description": property_record.description,
                    "postcode": property_record.postcode,
                    "state": property_record.state,
                }, status=200, message="Property found")
            else:
                return invalid_response("Property not found", status=404)
        except Exception as error:
            return invalid_response(str(error), status=500)

    # تحديث بيانات عقار بناءً على ID
    @http.route("/v2/property/<int:property_id>", methods=["PUT"], type="http", auth="none", csrf=False)
    def update_property(self, property_id):
        try:
            property_record = request.env['property'].sudo().search([("id", "=", property_id)], limit=1)
            if not property_record:
                return invalid_response("Property not found", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            property_record.write(vals)

            return valid_response({
                "id": property_record.id,
                "name": property_record.name,
            }, status=200, message="Property updated successfully")
        except json.JSONDecodeError:
            return invalid_response("Invalid JSON data", status=400)
        except Exception as error:
            return invalid_response(str(error), status=500)

    # حذف عقار بناءً على ID
    @http.route("/v2/property/<int:property_id>", methods=["DELETE"], type="http", auth="none", csrf=False)
    def delete_property(self, property_id):
        try:
            property_record = request.env['property'].sudo().search([("id", "=", property_id)], limit=1)
            if not property_record:
                return invalid_response("Property not found", status=404)

            property_record.unlink()
            return valid_response({}, status=200, message="Property deleted successfully")
        except Exception as error:
            return invalid_response(str(error), status=500)

    # استرجاع قائمة العقارات مع إمكانية التصفية بناءً على الحالة
    @http.route("/v2/properties", methods=["GET"], type="http", auth="none", csrf=False)
    def get_property_list(self):
        try:
            params = parse_qs(request.httprequest.query_string.decode('utf-8'))
            property_domain = []
            page = offset = None
            limit = 5
            if params:

                if params.get('limit'):
                    limit = int(params.get('limit')[0])
                    print(limit, "limit")
                if params.get('page'):
                    page = int(params.get('page')[0])
                    print(page, "page")
            if page:
                offset = (page * limit) - limit
                print(offset, "offset")

            # تصفية العقارات بناءً على الحالة إذا تم توفيرها
            if params.get('state'):
                property_domain.append(('state', '=', params['state'][0]))

            property_records = request.env['property'].sudo().search(property_domain, offset=offset, limit=limit,
                                                                     order="id desc")
            property_records_count = request.env['property'].sudo().search_count(property_domain)
            print(property_records)
            print(property_records_count)

            if not property_records:
                return invalid_response("No properties found", status=404)

            data = [{
                "id": record.id,
                "name": record.name,
                "description": record.description,
                "postcode": record.postcode,
                "state": record.state,
            } for record in property_records]
            pagination_info = {
                "page": page if page else 1,
                "limit": limit,
                "pages": math.ceil(property_records_count / limit) if limit else 1,
                "count": property_records_count,

            }

            return valid_response(data, pagination_info, status=200, message="Properties retrieved successfully")

        except Exception as error:

            return invalid_response(str(error), status=500)

    # @http.route("/v3/property", methods=["POST"], type="http", auth="none", csrf=False)
    # def create_property(self):
    #     try:
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #
    #         # التحقق من وجود الحقول المطلوبة
    #         if not vals.get("name"):
    #             return invalid_response("Field 'name' is required", status=400)
    #
    #         # إنشاء السجل
    #         # res = request.env["property"].sudo().create(vals)
    #
    #         cr = request.env.cr
    #
    #         print(cr)
    #         # query static
    #         # query = """
    #         # INSERT INTO property (name, postcode)
    #         # VALUES ('sql re', '123355')
    #         # RETURNING id, name, postcode;"""
    #
    #         columns = ','.join(vals.keys())
    #         values = ','.join(['%s'] * len(vals))
    #
    #         query = f"""
    #                   INSERT INTO property ({columns})
    #                   VALUES ({values})
    #                   RETURNING id, name, postcode;"""
    #         cr.execute(query, tuple(vals.values()))
    #         res = cr.fetchone()
    #         print(res)
    #
    #         if res:
    #             return valid_response({
    #                 "id": res[0],
    #                 "name": res[1],
    #                 "postcode": res[2],
    #             }, status=201, message="Property created successfully")
    #     except json.JSONDecodeError:
    #         return invalid_response("Invalid JSON data", status=400)
    #     except Exception as error:
    #         return invalid_response(str(error), status=500)


    # @http.route("/v3/property", methods=["POST"], type="json", auth="none", csrf=False)
    @http.route("/v3/property", methods=["POST"], type="http", auth="none", csrf=False)
    def create_property(self):
        try:
            # قراءة البيانات المرسلة عبر JSON
            vals = request.jsonrequest

            # التحقق من وجود الحقول المطلوبة
            if not vals or not vals.get("name"):
                return Response(
                    json.dumps({"status": 400, "message": "Field 'name' is required"}),
                    content_type='application/json',
                    status=400
                )

            # الحصول على Cursor لقاعدة البيانات
            cr = request.env.cr

            # بناء استعلام SQL ديناميكي
            columns = ', '.join(vals.keys())
            values = ', '.join(['%s'] * len(vals))

            query = f"""
                INSERT INTO property ({columns})
                VALUES ({values})
                RETURNING id, name, postcode;
            """

            # تنفيذ الاستعلام
            cr.execute(query, tuple(vals.values()))
            res = cr.fetchone()

            # التحقق من النتيجة وإرجاع استجابة ناجحة
            if res:
                return Response(
                    json.dumps({
                        "status": 201,
                        "message": "Property created successfully",
                        "data": {
                            "id": res[0],
                            "name": res[1],
                            "postcode": res[2],
                        }
                    }),
                    content_type='application/json',
                    status=201
                )
            else:
                return Response(
                    json.dumps({"status": 500, "message": "Failed to create property"}),
                    content_type='application/json',
                    status=500
                )

        except json.JSONDecodeError:
            return Response(
                json.dumps({"status": 400, "message": "Invalid JSON data"}),
                content_type='application/json',
                status=400
            )
        except Exception as error:
            return Response(
                json.dumps({"status": 500, "message": str(error)}),
                content_type='application/json',
                status=500
            )
