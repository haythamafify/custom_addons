# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class PropertyController(http.Controller):
    """
    Property API Controller
    =======================
    RESTful API for Property Management
    """

    def _authenticate_user(self):
        """
        Authenticate user from Basic Auth header
        Returns: user object or None
        """
        auth_header = request.httprequest.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Basic '):
            _logger.error("❌ No Authorization header")
            return None

        try:
            import base64
            import passlib.context

            # Decode Basic Auth
            auth_decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = auth_decoded.split(':', 1)

            _logger.info(f"🔍 Authenticating: {username}")

            # Find user
            user = request.env['res.users'].sudo().search([
                ('login', '=', username),
                ('active', '=', True)
            ], limit=1)

            if not user:
                _logger.error(f"❌ User not found: {username}")
                return None

            # Get password hash from database
            request.env.cr.execute(
                "SELECT password FROM res_users WHERE id = %s",
                (user.id,)
            )
            result = request.env.cr.fetchone()

            if not result or not result[0]:
                _logger.error("❌ No password set")
                return None

            stored_hash = result[0]

            # Verify password using passlib
            crypt_context = passlib.context.CryptContext(
                schemes=['pbkdf2_sha512', 'plaintext'],
                deprecated=['plaintext']
            )

            if crypt_context.verify(password, stored_hash):
                _logger.info(f"✅ Authentication SUCCESS: {user.name}")
                return user
            else:
                _logger.error("❌ Invalid password")
                return None

        except Exception as e:
            _logger.error(f"❌ Auth error: {str(e)}", exc_info=True)
            return None

    @http.route('/v1/property', methods=['POST'], type='http', auth='public', csrf=False)
    def post_property(self, **kwargs):
        """
        Create a new property via API

        Authentication: HTTP Basic Auth
        """
        _logger.info("=" * 50)
        _logger.info("📥 POST /v1/property")

        # Authenticate
        user = self._authenticate_user()
        if not user:
            return request.make_json_response(
                {"status": "error", "message": "Authentication required"},
                status=401
            )

        _logger.info(f"✅ User: {user.name}")

        # Parse JSON
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            _logger.info(f"📋 Data: {vals}")
        except json.JSONDecodeError as e:
            return request.make_json_response(
                {"status": "error", "message": "Invalid JSON"},
                status=400
            )

        # Add currency if missing
        if not vals.get("currency_id"):
            company = request.env['res.company'].sudo().search([], limit=1)
            if company and company.currency_id:
                vals["currency_id"] = company.currency_id.id

        # Create property
        try:
            # Use authenticated user's environment
            user_env = request.env(user=user.id)
            res = user_env["property"].sudo().create(vals)

            _logger.info(f"✅ Created: {res.name} (ID: {res.id})")

            return request.make_json_response({
                "status": "success",
                "id": res.id,
                "name": res.name,
                "ref": res.ref,
                "state": res.state,
                "created_by": user.name
            }, status=201)

        except Exception as e:
            _logger.error(f"❌ Error: {str(e)}", exc_info=True)
            return request.make_json_response(
                {"status": "error", "message": str(e)},
                status=400
            )

    @http.route('/v1/property/<int:property_id>', methods=['GET'], type='http', auth='public', csrf=False)
    def get_property(self, property_id, **kwargs):
        """Get property by ID"""
        user = self._authenticate_user()
        if not user:
            return request.make_json_response(
                {"status": "error", "message": "Authentication required"},
                status=401
            )

        try:
            prop = request.env["property"].sudo().browse(property_id)

            if not prop.exists():
                return request.make_json_response(
                    {"status": "error", "message": "Property not found"},
                    status=404
                )

            return request.make_json_response({
                "status": "success",
                "data": {
                    "id": prop.id,
                    "name": prop.name,
                    "ref": prop.ref,
                    "postcode": prop.postcode,
                    "state": prop.state,
                    "expected_price": prop.expected_price,
                    "selling_price": prop.selling_price,
                    "bedrooms": prop.bedrooms,
                    "owner": prop.owner_id.name if prop.owner_id else None
                }
            })

        except Exception as e:
            return request.make_json_response(
                {"status": "error", "message": str(e)},
                status=400
            )

    @http.route('/v1/property', methods=['GET'], type='http', auth='public', csrf=False)
    def get_all_properties(self, **kwargs):
        """Get all properties"""
        user = self._authenticate_user()
        if not user:
            return request.make_json_response(
                {"status": "error", "message": "Authentication required"},
                status=401
            )

        try:
            properties = request.env["property"].sudo().search([])

            data = [{
                "id": p.id,
                "name": p.name,
                "ref": p.ref,
                "state": p.state,
                "expected_price": p.expected_price
            } for p in properties]

            return request.make_json_response({
                "status": "success",
                "count": len(data),
                "data": data
            })

        except Exception as e:
            return request.make_json_response(
                {"status": "error", "message": str(e)},
                status=400
            )

    @http.route('/v1/property', methods=['GET'], type='http', auth='public', csrf=False)
    def get_all_properties(self, **kwargs):
        """
        Get all properties with optional filtering

        Query Parameters:
            - state: Filter by property state (new, offer_received, offer_accepted, sold, canceled)
            - postcode: Filter by postcode
            - bedrooms: Filter by minimum number of bedrooms

        Examples:
            GET /v1/property
            GET /v1/property?state=new
            GET /v1/property?state=offer_accepted
            GET /v1/property?state=sold&bedrooms=3
        """
        user = self._authenticate_user()
        if not user:
            return request.make_json_response(
                {"status": "error", "message": "Authentication required"},
                status=401
            )

        try:
            # بناء شروط البحث (domain)
            domain = []

            # فلترة حسب الحالة (state)
            if kwargs.get('state'):
                domain.append(('state', '=', kwargs['state']))
                _logger.info(f"🔍 Filtering by state: {kwargs['state']}")

            # فلترة حسب الـ postcode (إختياري)
            if kwargs.get('postcode'):
                domain.append(('postcode', '=', kwargs['postcode']))
                _logger.info(f"🔍 Filtering by postcode: {kwargs['postcode']}")

            # فلترة حسب عدد الغرف (إختياري)
            if kwargs.get('bedrooms'):
                try:
                    bedrooms = int(kwargs['bedrooms'])
                    domain.append(('bedrooms', '>=', bedrooms))
                    _logger.info(f"🔍 Filtering by bedrooms >= {bedrooms}")
                except ValueError:
                    pass

            # البحث في قاعدة البيانات
            properties = request.env["property"].sudo().search(domain)

            _logger.info(f"✅ Found {len(properties)} properties")

            # تجهيز البيانات للإرسال
            data = [{
                "id": p.id,
                "name": p.name,
                "ref": p.ref,
                "state": p.state,
                "postcode": p.postcode,
                "bedrooms": p.bedrooms,
                "expected_price": p.expected_price,
                "selling_price": p.selling_price,
                "owner": p.owner_id.name if p.owner_id else None
            } for p in properties]

            return request.make_json_response({
                "status": "success",
                "count": len(data),
                "filters": kwargs,  # إظهار الفلاتر المستخدمة
                "data": data
            })

        except Exception as e:
            _logger.error(f"❌ Search Error: {str(e)}", exc_info=True)
            return request.make_json_response(
                {"status": "error", "message": str(e)},
                status=400
            )

    @http.route('/v1/property', methods=['GET'], type='http', auth='public', csrf=False)
    def get_all_properties(self, **kwargs):
        """
        Get all properties with advanced filtering, sorting, and pagination

        Query Parameters:
            Filtering:
                - state: Filter by property state (draft, sold, etc.)
                - postcode: Filter by postcode
                - bedrooms: Filter by exact number of bedrooms
                - bedrooms_min: Minimum bedrooms
                - bedrooms_max: Maximum bedrooms
                - price_min: Minimum expected price
                - price_max: Maximum expected price
                - search: Search in name, ref, and postcode

            Sorting:
                - sort: Field to sort by (name, expected_price, bedrooms, etc.)
                - order: Sort order (asc or desc), default: asc

            Pagination:
                - page: Page number (starts from 1), default: 1
                - limit: Items per page, default: 10, max: 100

        Examples:
            GET /v1/property
            GET /v1/property?state=draft
            GET /v1/property?price_min=100000&price_max=500000
            GET /v1/property?search=villa
            GET /v1/property?sort=expected_price&order=desc
            GET /v1/property?page=2&limit=20
            GET /v1/property?state=draft&bedrooms_min=3&sort=expected_price&page=1&limit=10
        """
        user = self._authenticate_user()
        if not user:
            return request.make_json_response(
                {"status": "error", "message": "Authentication required"},
                status=401
            )

        try:
            # ========================================
            # 1. بناء شروط البحث (Domain)
            # ========================================
            domain = []

            # فلترة حسب الحالة (state)
            if kwargs.get('state'):
                domain.append(('state', '=', kwargs['state']))
                _logger.info(f"🔍 Filtering by state: {kwargs['state']}")

            # فلترة حسب الـ postcode
            if kwargs.get('postcode'):
                domain.append(('postcode', '=', kwargs['postcode']))
                _logger.info(f"🔍 Filtering by postcode: {kwargs['postcode']}")

            # ========================================
            # 2. فلترة عدد الغرف (Bedrooms)
            # ========================================

            # عدد غرف محدد بالضبط
            if kwargs.get('bedrooms'):
                try:
                    bedrooms = int(kwargs['bedrooms'])
                    domain.append(('bedrooms', '=', bedrooms))
                    _logger.info(f"🔍 Filtering by bedrooms = {bedrooms}")
                except ValueError:
                    pass

            # حد أدنى لعدد الغرف
            if kwargs.get('bedrooms_min'):
                try:
                    bedrooms_min = int(kwargs['bedrooms_min'])
                    domain.append(('bedrooms', '>=', bedrooms_min))
                    _logger.info(f"🔍 Filtering by bedrooms >= {bedrooms_min}")
                except ValueError:
                    pass

            # حد أقصى لعدد الغرف
            if kwargs.get('bedrooms_max'):
                try:
                    bedrooms_max = int(kwargs['bedrooms_max'])
                    domain.append(('bedrooms', '<=', bedrooms_max))
                    _logger.info(f"🔍 Filtering by bedrooms <= {bedrooms_max}")
                except ValueError:
                    pass

            # ========================================
            # 3. فلترة السعر المتوقع (Price Range)
            # ========================================

            # حد أدنى للسعر
            if kwargs.get('price_min'):
                try:
                    price_min = float(kwargs['price_min'])
                    domain.append(('expected_price', '>=', price_min))
                    _logger.info(f"🔍 Filtering by price >= {price_min}")
                except ValueError:
                    pass

            # حد أقصى للسعر
            if kwargs.get('price_max'):
                try:
                    price_max = float(kwargs['price_max'])
                    domain.append(('expected_price', '<=', price_max))
                    _logger.info(f"🔍 Filtering by price <= {price_max}")
                except ValueError:
                    pass

            # ========================================
            # 4. البحث النصي (Text Search)
            # ========================================

            if kwargs.get('search'):
                search_term = kwargs['search']
                # البحث في name أو ref أو postcode
                domain.append('|')  # OR operator
                domain.append('|')
                domain.append(('name', 'ilike', search_term))
                domain.append(('ref', 'ilike', search_term))
                domain.append(('postcode', 'ilike', search_term))
                _logger.info(f"🔍 Searching for: {search_term}")

            # ========================================
            # 5. الترتيب (Sorting)
            # ========================================

            # الحقول المسموح بالترتيب عليها
            allowed_sort_fields = ['name', 'expected_price', 'selling_price',
                                   'bedrooms', 'postcode', 'state', 'create_date']

            sort_field = kwargs.get('sort', 'id')  # default: id
            sort_order = kwargs.get('order', 'asc')  # default: ascending

            # التحقق من صحة الحقل
            if sort_field not in allowed_sort_fields and sort_field != 'id':
                sort_field = 'id'

            # التحقق من صحة الاتجاه
            if sort_order not in ['asc', 'desc']:
                sort_order = 'asc'

            # بناء نص الترتيب
            order_string = f"{sort_field} {sort_order}"
            _logger.info(f"📊 Sorting by: {order_string}")

            # ========================================
            # 6. Pagination (التقسيم لصفحات)
            # ========================================

            # استخراج معاملات الصفحة
            try:
                page = int(kwargs.get('page', 1))
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            try:
                limit = int(kwargs.get('limit', 10))
                # حد أقصى 100 عنصر لكل صفحة
                if limit < 1:
                    limit = 10
                elif limit > 100:
                    limit = 100
            except ValueError:
                limit = 10

            # حساب الـ offset
            offset = (page - 1) * limit

            _logger.info(f"📄 Page {page}, Limit {limit}, Offset {offset}")

            # ========================================
            # 7. البحث في قاعدة البيانات
            # ========================================

            # عد إجمالي النتائج (بدون pagination)
            total_count = request.env["property"].sudo().search_count(domain)

            # جلب البيانات مع pagination و sorting
            properties = request.env["property"].sudo().search(
                domain,
                order=order_string,
                limit=limit,
                offset=offset
            )

            _logger.info(f"✅ Found {len(properties)} properties (Total: {total_count})")

            # ========================================
            # 8. تجهيز البيانات للإرسال
            # ========================================

            data = [{
                "id": p.id,
                "name": p.name,
                "ref": p.ref,
                "state": p.state,
                "postcode": p.postcode,
                "bedrooms": p.bedrooms,
                "expected_price": p.expected_price,
                "selling_price": p.selling_price,
                "owner": p.owner_id.name if p.owner_id else None
            } for p in properties]

            # ========================================
            # 9. حساب معلومات الـ Pagination
            # ========================================

            total_pages = (total_count + limit - 1) // limit  # ceiling division
            has_next = page < total_pages
            has_prev = page > 1

            # ========================================
            # 10. إرجاع النتيجة
            # ========================================

            return request.make_json_response({
                "status": "success",
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_items": total_count,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_prev": has_prev,
                    "items_in_page": len(data)
                },
                "filters": {
                    "state": kwargs.get('state'),
                    "postcode": kwargs.get('postcode'),
                    "bedrooms": kwargs.get('bedrooms'),
                    "bedrooms_min": kwargs.get('bedrooms_min'),
                    "bedrooms_max": kwargs.get('bedrooms_max'),
                    "price_min": kwargs.get('price_min'),
                    "price_max": kwargs.get('price_max'),
                    "search": kwargs.get('search')
                },
                "sorting": {
                    "field": sort_field,
                    "order": sort_order
                },
                "data": data
            })

        except Exception as e:
            _logger.error(f"❌ Search Error: {str(e)}", exc_info=True)
            return request.make_json_response(
                {"status": "error", "message": str(e)},
                status=400
            )

    @http.route('/v1/property/<int:property_id>', methods=['PUT'], type='http', auth='public', csrf=False)
    def update_property(self, property_id, **kwargs):
        """
        Update an existing property via API

        Authentication: HTTP Basic Auth
        URL Parameter: property_id (int)
        Body: JSON with fields to update

        Example:
            PUT /v1/property/5
            {
                "expected_price": 250000,
                "bedrooms": 4,
                "state": "offer_accepted"
            }
        """
        _logger.info("=" * 50)
        _logger.info(f" PUT /v1/property/{property_id}")

        # Authenticate user
        user = self._authenticate_user()
        if not user:
            return request.make_json_response(
                {"status": "error", "message": "Authentication required"},
                status=401
            )

        _logger.info(f"✅ User: {user.name}")

        # Parse JSON body
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            _logger.info(f"📋 Update Data: {vals}")
        except json.JSONDecodeError as e:
            return request.make_json_response(
                {"status": "error", "message": "Invalid JSON"},
                status=400
            )

        # Validate that there's data to update
        if not vals:
            return request.make_json_response(
                {"status": "error", "message": "No data provided for update"},
                status=400
            )

        try:
            # Find property
            prop = request.env["property"].sudo().browse(property_id)

            if not prop.exists():
                return request.make_json_response(
                    {"status": "error", "message": "Property not found"},
                    status=404
                )

            # Store old values for logging
            old_name = prop.name

            # Update property with authenticated user's environment
            user_env = request.env(user=user.id)
            prop_user_env = user_env["property"].sudo().browse(property_id)
            prop_user_env.write(vals)

            _logger.info(f"✅ Updated: {old_name} → {prop.name} (ID: {prop.id})")

            # Return updated property data
            return request.make_json_response({
                "status": "success",
                "message": "Property updated successfully",
                "data": {
                    "id": prop.id,
                    "name": prop.name,
                    "ref": prop.ref,
                    "postcode": prop.postcode,
                    "state": prop.state,
                    "expected_price": prop.expected_price,
                    "selling_price": prop.selling_price,
                    "bedrooms": prop.bedrooms,
                    "owner": prop.owner_id.name if prop.owner_id else None
                },
                "updated_by": user.name
            })

        except Exception as e:
            _logger.error(f"❌ Update Error: {str(e)}", exc_info=True)
            return request.make_json_response(
                {"status": "error", "message": str(e)},
                status=400
            )

    @http.route('/v1/property/<int:property_id>', methods=['DELETE'], type='http', auth='public', csrf=False)
    def delete_property(self, property_id, **kwargs):
        """Delete a property"""
        user = self._authenticate_user()
        if not user:
            return request.make_json_response(
                {"status": "error", "message": "Authentication required"},
                status=401
            )

        try:
            prop = request.env["property"].sudo().browse(property_id)

            if not prop.exists():
                return request.make_json_response(
                    {"status": "error", "message": "Property not found"},
                    status=404
                )

            prop_name = prop.name
            prop.unlink()

            _logger.info(f"🗑️ Deleted: {prop_name} (ID: {property_id})")

            return request.make_json_response({
                "status": "success",
                "message": f"Property '{prop_name}' deleted successfully",
                "deleted_by": user.name
            })

        except Exception as e:
            _logger.error(f"❌ Delete Error: {str(e)}", exc_info=True)
            return request.make_json_response(
                {"status": "error", "message": str(e)},
                status=400
            )
