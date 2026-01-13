# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError
import json
import logging
import base64
from functools import wraps

_logger = logging.getLogger(__name__)


def validate_auth(func):
    """
    Decorator to validate authentication for all routes
    Reduces code duplication
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        user = self._authenticate_user()
        if not user:
            return self._error_response(
                "Authentication required",
                status=401
            )
        return func(self, user=user, *args, **kwargs)

    return wrapper


class PropertyController(http.Controller):
    """
    RESTful API Controller for Property Management

    All endpoints require HTTP Basic Authentication
    Base URL: /v1/property
    """

    # ========================================
    # Helper Methods
    # ========================================

    def _authenticate_user(self):
        """
        Authenticate user using HTTP Basic Auth

        Returns:
            res.users recordset or None
        """
        auth_header = request.httprequest.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Basic '):
            _logger.warning("Missing or invalid Authorization header")
            return None

        try:
            # Decode credentials
            credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = credentials.split(':', 1)

            # Find active user
            user = request.env['res.users'].sudo().search([
                ('login', '=', username),
                ('active', '=', True)
            ], limit=1)

            if not user:
                _logger.warning(f"User not found: {username}")
                return None

            # Get password hash from database
            request.env.cr.execute(
                "SELECT password FROM res_users WHERE id = %s",
                (user.id,)
            )
            result = request.env.cr.fetchone()

            if not result or not result[0]:
                _logger.warning(f"No password set for user: {username}")
                return None

            stored_hash = result[0]

            # Verify password using passlib
            try:
                from passlib.context import CryptContext

                pwd_context = CryptContext(
                    schemes=['pbkdf2_sha512', 'plaintext'],
                    deprecated=['plaintext']
                )

                if pwd_context.verify(password, stored_hash):
                    _logger.info(f"Authentication successful: {user.login}")
                    return user
                else:
                    _logger.warning(f"Invalid password for user: {username}")
                    return None

            except Exception as pwd_error:
                _logger.error(f"Password verification failed: {str(pwd_error)}")
                return None

        except Exception as e:
            _logger.error(f"Authentication error: {str(e)}", exc_info=True)
            return None

    def _success_response(self, data, status=200):
        """Return standardized success response"""
        return request.make_json_response({
            "status": "success",
            "data": data
        }, status=status)

    def _error_response(self, message, status=400, details=None):
        """Return standardized error response"""
        response = {
            "status": "error",
            "message": message
        }
        if details:
            response["details"] = details
        return request.make_json_response(response, status=status)

    def _parse_json_body(self):
        """
        Parse and validate JSON request body

        Returns:
            dict or None
        """
        try:
            body = request.httprequest.data.decode('utf-8')
            if not body:
                return {}
            return json.loads(body)
        except json.JSONDecodeError as e:
            _logger.error(f"Invalid JSON: {str(e)}")
            return None
        except Exception as e:
            _logger.error(f"Error parsing body: {str(e)}")
            return None

    def _build_property_data(self, prop):
        """
        Build standardized property data dictionary

        Args:
            prop: property recordset

        Returns:
            dict
        """
        try:
            return {
                "id": prop.id,
                "name": prop.name,
                "ref": prop.ref if prop.ref else None,
                "postcode": prop.postcode if prop.postcode else None,
                "state": prop.state if hasattr(prop, 'state') else None,
                "expected_price": prop.expected_price if prop.expected_price else 0,
                "selling_price": prop.selling_price if prop.selling_price else 0,
                "bedrooms": prop.bedrooms if prop.bedrooms else 0,
                "living_area": prop.living_area if hasattr(prop, 'living_area') and prop.living_area else 0,
                "garden": prop.garden if hasattr(prop, 'garden') else False,
                "owner": prop.owner_id.name if prop.owner_id else None
            }
        except Exception as e:
            _logger.error(f"Error building property data: {str(e)}")
            return {
                "id": prop.id,
                "name": prop.name,
                "error": "Some fields could not be loaded"
            }

    def _validate_property_data(self, data, is_update=False):
        """
        Validate property data before create/update

        Args:
            data: dict of property values
            is_update: bool, True for update operations

        Returns:
            tuple (is_valid: bool, error_message: str or None)
        """
        if not is_update:
            # Required fields for creation (based on property model)
            required_fields = ['name', 'postcode']
            for field in required_fields:
                if field not in data:
                    return False, f"Missing required field: {field}"

        # Validate data types
        if 'expected_price' in data:
            try:
                price = float(data['expected_price'])
                if price < 0:
                    return False, "expected_price must be positive"
            except (ValueError, TypeError):
                return False, "expected_price must be a number"

        if 'bedrooms' in data:
            try:
                bedrooms = int(data['bedrooms'])
                if bedrooms < 0:
                    return False, "bedrooms must be positive"
            except (ValueError, TypeError):
                return False, "bedrooms must be an integer"

        if 'living_area' in data:
            try:
                area = int(data['living_area'])
                if area < 0:
                    return False, "living_area must be positive"
            except (ValueError, TypeError):
                return False, "living_area must be an integer"

        return True, None

    def _build_search_domain(self, params):
        """
        Build Odoo search domain from query parameters

        Args:
            params: dict of query parameters

        Returns:
            list: Odoo domain
        """
        domain = []

        # Filter by state
        if params.get('state'):
            domain.append(('state', '=', params['state']))

        # Filter by postcode
        if params.get('postcode'):
            domain.append(('postcode', '=', params['postcode']))

        # Filter by exact bedrooms
        if params.get('bedrooms'):
            try:
                domain.append(('bedrooms', '=', int(params['bedrooms'])))
            except ValueError:
                pass

        # Filter by minimum bedrooms
        if params.get('bedrooms_min'):
            try:
                domain.append(('bedrooms', '>=', int(params['bedrooms_min'])))
            except ValueError:
                pass

        # Filter by maximum bedrooms
        if params.get('bedrooms_max'):
            try:
                domain.append(('bedrooms', '<=', int(params['bedrooms_max'])))
            except ValueError:
                pass

        # Filter by minimum price
        if params.get('price_min'):
            try:
                domain.append(('expected_price', '>=', float(params['price_min'])))
            except ValueError:
                pass

        # Filter by maximum price
        if params.get('price_max'):
            try:
                domain.append(('expected_price', '<=', float(params['price_max'])))
            except ValueError:
                pass

        # Text search in name, ref, and postcode
        if params.get('search'):
            search_term = params['search']
            domain.extend([
                '|', '|',
                ('name', 'ilike', search_term),
                ('ref', 'ilike', search_term),
                ('postcode', 'ilike', search_term)
            ])

        return domain

    def _get_sort_order(self, params):
        """
        Get validated sort order string

        Args:
            params: dict of query parameters

        Returns:
            str: sort order (e.g., 'name asc')
        """
        allowed_fields = [
            'name', 'expected_price', 'selling_price',
            'bedrooms', 'postcode', 'state', 'create_date', 'id'
        ]

        sort_field = params.get('sort', 'id')
        sort_order = params.get('order', 'asc')

        # Validate field
        if sort_field not in allowed_fields:
            sort_field = 'id'

        # Validate order
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'

        return f"{sort_field} {sort_order}"

    def _get_pagination_params(self, params):
        """
        Get validated pagination parameters

        Args:
            params: dict of query parameters

        Returns:
            tuple (page: int, limit: int, offset: int)
        """
        try:
            page = int(params.get('page', 1))
            page = max(1, page)
        except ValueError:
            page = 1

        try:
            limit = int(params.get('limit', 10))
            limit = max(1, min(100, limit))
        except ValueError:
            limit = 10

        offset = (page - 1) * limit

        return page, limit, offset

    # ========================================
    # API Endpoints
    # ========================================

    @http.route('/v1/property', methods=['POST'], type='http', auth='public', csrf=False)
    @validate_auth
    def create_property(self, user=None, **kwargs):
        """
        Create a new property

        Request Body:
            {
                "name": "Villa Name",
                "postcode": "12345",
                "expected_price": 500000,
                "bedrooms": 4
            }

        Returns:
            201: Property created successfully
            400: Invalid data
            401: Authentication required
        """
        _logger.info(f"POST /v1/property by user: {user.login}")

        # Parse JSON body
        vals = self._parse_json_body()
        if vals is None:
            return self._error_response("Invalid JSON format", status=400)

        # Validate data
        is_valid, error_msg = self._validate_property_data(vals)
        if not is_valid:
            return self._error_response(error_msg, status=400)

        # Add default currency if missing
        if 'currency_id' not in vals:
            try:
                company = request.env['res.company'].sudo().search([], limit=1)
                if company and company.currency_id:
                    vals['currency_id'] = company.currency_id.id
            except Exception as e:
                _logger.warning(f"Could not set default currency: {e}")

        try:
            # Create property with user context
            Property = request.env(user=user.id)['property'].sudo()
            prop = Property.create(vals)

            _logger.info(f"Property created: {prop.name} (ID: {prop.id})")

            return self._success_response({
                "id": prop.id,
                "name": prop.name,
                "ref": prop.ref if prop.ref else None,
                "state": prop.state if hasattr(prop, 'state') else None,
                "postcode": prop.postcode,
                "created_by": user.name
            }, status=201)

        except ValidationError as e:
            _logger.warning(f"Validation error: {str(e)}")
            error_msg = str(e).replace('\n', ' ').strip()
            return self._error_response(error_msg, status=400)
        except KeyError as e:
            _logger.error(f"Model not found: {str(e)}")
            return self._error_response(f"Property model not found: {str(e)}", status=500)
        except Exception as e:
            _logger.error(f"Error creating property: {str(e)}", exc_info=True)
            return self._error_response(f"Failed to create property: {str(e)}", status=500)

    @http.route('/v1/property/<int:property_id>', methods=['GET'], type='http', auth='public', csrf=False)
    @validate_auth
    def get_property(self, property_id, user=None, **kwargs):
        """
        Get a single property by ID

        Returns:
            200: Property data
            404: Property not found
            401: Authentication required
        """
        try:
            prop = request.env['property'].sudo().browse(property_id)

            if not prop.exists():
                return self._error_response("Property not found", status=404)

            return self._success_response(self._build_property_data(prop))

        except Exception as e:
            _logger.error(f"Error fetching property {property_id}: {str(e)}", exc_info=True)
            return self._error_response("Failed to fetch property", status=500)

    @http.route('/v1/property', methods=['GET'], type='http', auth='public', csrf=False)
    @validate_auth
    def list_properties(self, user=None, **kwargs):
        """
        List properties with filtering, sorting, and pagination

        Query Parameters:
            Filtering:
                - state: Property state (draft, pending, sold, closed)
                - postcode: Exact postcode match
                - bedrooms: Exact number of bedrooms
                - bedrooms_min: Minimum bedrooms
                - bedrooms_max: Maximum bedrooms
                - price_min: Minimum expected price
                - price_max: Maximum expected price
                - search: Search in name, ref, postcode

            Sorting:
                - sort: Field name (default: id)
                - order: asc or desc (default: asc)

            Pagination:
                - page: Page number (default: 1)
                - limit: Items per page (default: 10, max: 100)

        Returns:
            200: List of properties with pagination info
            401: Authentication required
        """
        try:
            # Build search domain
            domain = self._build_search_domain(kwargs)

            # Get sort order
            order = self._get_sort_order(kwargs)

            # Get pagination params
            page, limit, offset = self._get_pagination_params(kwargs)

            # Count total results
            Property = request.env['property'].sudo()
            total_count = Property.search_count(domain)

            # Fetch paginated results
            properties = Property.search(
                domain,
                order=order,
                limit=limit,
                offset=offset
            )

            # Build response data
            data = [self._build_property_data(p) for p in properties]

            # Calculate pagination metadata
            total_pages = (total_count + limit - 1) // limit

            return self._success_response({
                "items": data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_items": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
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
                "sort": {
                    "field": kwargs.get('sort', 'id'),
                    "order": kwargs.get('order', 'asc')
                }
            })

        except Exception as e:
            _logger.error(f"Error listing properties: {str(e)}", exc_info=True)
            return self._error_response("Failed to list properties", status=500)

    @http.route('/v1/property/<int:property_id>', methods=['PUT'], type='http', auth='public', csrf=False)
    @validate_auth
    def update_property(self, property_id, user=None, **kwargs):
        """
        Update an existing property

        Request Body:
            {
                "expected_price": 250000,
                "bedrooms": 4
            }

        Returns:
            200: Property updated successfully
            400: Invalid data
            404: Property not found
            401: Authentication required
        """
        _logger.info(f"PUT /v1/property/{property_id} by user: {user.login}")

        # Parse JSON body
        vals = self._parse_json_body()
        if vals is None:
            return self._error_response("Invalid JSON format", status=400)

        if not vals:
            return self._error_response("No data provided for update", status=400)

        # Validate data
        is_valid, error_msg = self._validate_property_data(vals, is_update=True)
        if not is_valid:
            return self._error_response(error_msg, status=400)

        try:
            # Find property
            prop = request.env['property'].sudo().browse(property_id)

            if not prop.exists():
                return self._error_response("Property not found", status=404)

            # Update with user context
            Property = request.env(user=user.id)['property'].sudo()
            prop_to_update = Property.browse(property_id)
            prop_to_update.write(vals)

            _logger.info(f"Property updated: {prop.name} (ID: {prop.id})")

            return self._success_response({
                "property": self._build_property_data(prop),
                "updated_by": user.name
            })

        except ValidationError as e:
            _logger.warning(f"Validation error: {str(e)}")
            error_msg = str(e).replace('\n', ' ').strip()
            return self._error_response(error_msg, status=400)
        except Exception as e:
            _logger.error(f"Error updating property {property_id}: {str(e)}", exc_info=True)
            return self._error_response(f"Failed to update property: {str(e)}", status=500)

    @http.route('/v1/property/<int:property_id>', methods=['DELETE'], type='http', auth='public', csrf=False)
    @validate_auth
    def delete_property(self, property_id, user=None, **kwargs):
        """
        Delete a property

        Returns:
            200: Property deleted successfully
            404: Property not found
            401: Authentication required
        """
        _logger.info(f"DELETE /v1/property/{property_id} by user: {user.login}")

        try:
            prop = request.env['property'].sudo().browse(property_id)

            if not prop.exists():
                return self._error_response("Property not found", status=404)

            prop_name = prop.name
            prop.unlink()

            _logger.info(f"Property deleted: {prop_name} (ID: {property_id})")

            return self._success_response({
                "message": f"Property '{prop_name}' deleted successfully",
                "deleted_by": user.name
            })

        except Exception as e:
            _logger.error(f"Error deleting property {property_id}: {str(e)}", exc_info=True)
            return self._error_response(f"Failed to delete property: {str(e)}", status=500)

    # ========================================
    # Debug/Test Endpoints
    # ========================================

    @http.route('/test/property/create', methods=['POST'], type='http', auth='public', csrf=False)
    def test_create_debug(self, **kwargs):
        """Debug endpoint for testing property creation"""
        try:
            _logger.info("=" * 60)
            _logger.info("DEBUG: Test Create Property")
            _logger.info("=" * 60)

            body = request.httprequest.data.decode('utf-8')
            _logger.info(f"Raw body: {body}")

            vals = json.loads(body) if body else {}
            _logger.info(f"Parsed vals: {vals}")

            # Add required fields if missing
            if 'name' not in vals:
                vals['name'] = 'Test Property'
            if 'postcode' not in vals:
                vals['postcode'] = '00000'

            _logger.info(f"Final vals: {vals}")

            prop = request.env['property'].sudo().create(vals)

            _logger.info(f"SUCCESS! Created property ID: {prop.id}")
            _logger.info("=" * 60)

            return request.make_json_response({
                "status": "success",
                "message": "Property created successfully",
                "data": {
                    "id": prop.id,
                    "name": prop.name,
                    "ref": prop.ref if prop.ref else None,
                    "postcode": prop.postcode
                }
            })

        except Exception as e:
            _logger.error(f"ERROR: {str(e)}", exc_info=True)
            _logger.info("=" * 60)

            return request.make_json_response({
                "status": "error",
                "message": str(e),
                "type": type(e).__name__
            }, status=500)