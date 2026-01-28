from odoo import http
import json
import logging

_logger = logging.getLogger(__name__)


class ResPartner(http.Controller):
    @http.route('/owl/rpc_service', type='http', auth='user', methods=['POST'], csrf=False)
    def get_customers(self, **kwargs):
        try:
            # Parse JSON body from request
            request_body = http.request.httprequest.get_data(as_text=True)
            
            if not request_body:
                _logger.warning("Empty request body received")
                data = {}
            else:
                data = json.loads(request_body)
            
            limit = int(data.get('limit', 15))
            
            _logger.info(f"Fetching partners with limit: {limit}")
            
            partners = http.request.env['res.partner'].search_read(
                [],
                ['id', 'name', 'email'],
                limit=limit
            )
            
            response_data = {
                'success': True,
                'data': partners,
                'message': f'Retrieved {len(partners)} partners'
            }
            
            return http.Response(
                json.dumps(response_data),
                status=200,
                content_type='application/json',
                headers={'Cache-Control': 'no-cache, no-store, must-revalidate'}
            )
        except json.JSONDecodeError as e:
            _logger.error(f"JSON decode error: {e}")
            response_data = {
                'success': False,
                'error': f'Invalid JSON: {str(e)}',
                'message': 'Failed to parse request'
            }
            return http.Response(
                json.dumps(response_data),
                status=400,
                content_type='application/json'
            )
        except Exception as e:
            _logger.error(f"Error in get_customers: {e}", exc_info=True)
            response_data = {
                'success': False,
                'error': str(e),
                'message': 'Error retrieving partners'
            }
            return http.Response(
                json.dumps(response_data),
                status=500,
                content_type='application/json'
            )