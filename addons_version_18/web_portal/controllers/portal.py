# -*- coding: utf-8 -*-
import json
import logging
from datetime import timedelta
from urllib.parse import urlencode

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)


class PropertyPortal(CustomerPortal):
    _items_per_page = 10

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'property_count' in counters:
            domain = self._get_property_domain()
            values['property_count'] = request.env['property'].search_count(domain)
        return values

    def _get_property_domain(self):
        """Limit properties to the current user."""
        return [('user_id', '=', request.env.user.id)]

    def _get_property_form_values(self, property_rec=None, errors=None, values=None):
        values = values or {}
        errors = errors or {}
        return {
            'page_name': 'property_form',
            'property': property_rec,
            'values': values,
            'errors': errors,
            'breadcrumbs': [
                {'name': _('Properties'), 'url': '/my/properties'},
                {'name': property_rec.name if property_rec else _('New Property'), 'active': True},
            ],
        }

    def _parse_property_form(self, kw):
        def _to_int(val):
            return int(val) if val not in (None, '', False) else 0

        def _to_float(val):
            return float(val) if val not in (None, '', False) else 0.0

        def _to_bool(val):
            return val in ('on', 'true', 'True', True, '1', 1)

        return {
            'name': (kw.get('name') or '').strip(),
            'description': (kw.get('description') or '').strip(),
            'postcode': (kw.get('postcode') or '').strip(),
            'expected_price': _to_float(kw.get('expected_price')),
            'bedrooms': _to_int(kw.get('bedrooms')),
            'living_area': _to_int(kw.get('living_area')),
            'facades': _to_int(kw.get('facades')),
            'garage': _to_bool(kw.get('garage')),
            'garden': _to_bool(kw.get('garden')),
            'garden_area': _to_int(kw.get('garden_area')),
            'garden_orientation': kw.get('garden_orientation') or 'north',
            'expected_date_selling': kw.get('expected_date_selling') or False,
        }

    def _validate_property_form(self, values):
        """
        Server-side validation for property form data.
        Returns a dictionary of errors. Empty dict means no errors.
        """
        errors = {}

        # Required field validation
        if not values.get('name'):
            errors['name'] = _('Name is required.')
        elif len(values.get('name', '').strip()) < 3:
            errors['name'] = _('Name must be at least 3 characters long.')
        elif len(values.get('name', '')) > 255:
            errors['name'] = _('Name cannot exceed 255 characters.')

        if not values.get('postcode'):
            errors['postcode'] = _('Postcode is required.')
        elif len(values.get('postcode', '').strip()) < 3:
            errors['postcode'] = _('Postcode must be at least 3 characters long.')
        elif len(values.get('postcode', '')) > 20:
            errors['postcode'] = _('Postcode cannot exceed 20 characters.')

        # Numeric fields validation
        if values.get('expected_price'):
            if values['expected_price'] < 0:
                errors['expected_price'] = _('Expected price cannot be negative.')
            elif values['expected_price'] > 99999999.99:
                errors['expected_price'] = _('Expected price is too high.')

        if values.get('bedrooms'):
            if values['bedrooms'] < 0:
                errors['bedrooms'] = _('Bedrooms cannot be negative.')
            elif values['bedrooms'] > 100:
                errors['bedrooms'] = _('Number of bedrooms is unrealistic.')

        if values.get('living_area'):
            if values['living_area'] < 0:
                errors['living_area'] = _('Living area cannot be negative.')
            elif values['living_area'] > 100000:
                errors['living_area'] = _('Living area is unrealistic.')

        if values.get('facades'):
            if values['facades'] < 0:
                errors['facades'] = _('Facades cannot be negative.')
            elif values['facades'] > 50:
                errors['facades'] = _('Number of facades is unrealistic.')

        if values.get('garden_area'):
            if values['garden_area'] < 0:
                errors['garden_area'] = _('Garden area cannot be negative.')
            elif values['garden_area'] > 100000:
                errors['garden_area'] = _('Garden area is unrealistic.')

        # Conditional validation: If garden is selected, garden_area should be provided
        if values.get('garden') and values.get('garden_area') == 0:
            errors['garden_area'] = _('Garden area is required when garden is selected.')

        # Garden orientation validation
        valid_orientations = ['north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest']
        if values.get('garden_orientation') not in valid_orientations:
            errors['garden_orientation'] = _('Invalid garden orientation.')

        # Description optional but has max length
        if values.get('description') and len(values['description']) > 2000:
            errors['description'] = _('Description cannot exceed 2000 characters.')

        # Date validation
        if values.get('expected_date_selling'):
            from datetime import datetime
            try:
                if isinstance(values['expected_date_selling'], str):
                    datetime.fromisoformat(values['expected_date_selling'])
            except (ValueError, TypeError):
                errors['expected_date_selling'] = _('Invalid date format.')

        return errors

    @http.route(['/my/properties', '/my/properties/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_properties(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        Property = request.env['property']
        domain = self._get_property_domain()

        sortby = kw.get('sortby') or 'newest'
        groupby = kw.get('groupby') or 'none'
        search = (kw.get('search') or '').strip()
        sort_options = [
            {'key': 'newest', 'label': _('Newest'), 'order': 'create_date desc'},
            {'key': 'name', 'label': _('Name'), 'order': 'name asc'},
            {'key': 'price', 'label': _('Expected Price'), 'order': 'expected_price desc'},
            {'key': 'state', 'label': _('State'), 'order': 'state asc'},
        ]
        group_options = [
            {'key': 'none', 'label': _('No Group')},
            {'key': 'state', 'label': _('State')},
            {'key': 'name', 'label': _('Name')},
        ]
        sortby_map = {opt['key']: opt['order'] for opt in sort_options}
        sort_order = sortby_map.get(sortby, sortby_map['newest'])
        groupby_map = {
            'state': 'state',
            'name': 'name',
        }
        groupby_field = groupby_map.get(groupby)

        if search:
            domain = domain + ['|', '|',
                               ('name', 'ilike', search),
                               ('ref', 'ilike', search),
                               ('state', 'ilike', search)]

        property_count = Property.search_count(domain)
        page_start = 0
        page_end = 0
        if property_count:
            page_start = ((page - 1) * self._items_per_page) + 1
            page_end = min(page * self._items_per_page, property_count)
        url_args = {}
        if sortby:
            url_args['sortby'] = sortby
        if groupby:
            url_args['groupby'] = groupby
        if search:
            url_args['search'] = search
        export_url = '/my/properties/xlsx_report'
        export_args = {}
        if search:
            export_args['search'] = search
        if export_args:
            export_url = '%s?%s' % (export_url, urlencode(export_args))

        def _make_page_url(page_number):
            base = '/my/properties' if page_number == 1 else '/my/properties/page/%s' % page_number
            if not url_args:
                return base
            query_string = '&'.join('%s=%s' % (key, url_args[key]) for key in sorted(url_args))
            return '%s?%s' % (base, query_string)

        pager = portal_pager(
            url='/my/properties',
            total=property_count,
            page=page,
            step=self._items_per_page,
            url_args=url_args,
        )
        page_count = pager.get('page_count', 1)
        page_links = [
            {
                'num': p,
                'url': _make_page_url(p)
            }
            for p in range(1, page_count + 1)
        ]
        prev_url = None
        next_url = None
        if page > 1:
            prev_url = _make_page_url(page - 1)
        if page < page_count:
            next_url = _make_page_url(page + 1)

        properties = Property.search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        grouped_properties = []
        if groupby_field:
            label_map = {}
            field_def = Property._fields.get(groupby_field)
            if field_def and getattr(field_def, 'selection', None):
                label_map = dict(field_def.selection)
            groups = {}
            for rec in properties:
                key = getattr(rec, groupby_field) or False
                label = label_map.get(key) or (key if key else _('Undefined'))
                if key not in groups:
                    groups[key] = {
                        'label': label,
                        'records': Property.browse(),
                    }
                groups[key]['records'] |= rec
            grouped_properties = sorted(
                groups.values(),
                key=lambda g: g['label'] or '',
            )

        values.update({
            'page_name': 'properties',
            'properties': properties,
            'grouped_properties': grouped_properties,
            'pager': pager,
            'property_count': property_count,
            'page_start': page_start,
            'page_end': page_end,
            'page_links': page_links,
            'prev_url': prev_url,
            'next_url': next_url,
            'default_url': '/my/properties',
            'export_url': export_url,
            'sortby': sortby,
            'sort_options': sort_options,
            'groupby': groupby,
            'group_options': group_options,
            'search': search,
            'breadcrumbs': [
                {'name': _('Properties'), 'active': True},
            ],
        })
        return request.render('web_portal.portal_my_properties', values)

    @http.route(['/my/properties/new'], type='http', auth='user', website=True, csrf=True, methods=['GET', 'POST'])
    def portal_property_create(self, **kw):
        if request.httprequest.method == 'POST':
            values = self._parse_property_form(kw)
            errors = self._validate_property_form(values)
            
            if errors:
                return request.render(
                    'web_portal.portal_property_form',
                    self._get_property_form_values(None, errors=errors, values=values)
                )

            values['user_id'] = request.env.user.id
            try:
                request.env['property'].create(values)
                return request.redirect('/my/properties')
            except Exception as exc:
                request.env.cr.rollback()
                errors['form'] = str(exc)
                _logger.error("Portal create property failed: %s", exc, exc_info=True)
                return request.render(
                    'web_portal.portal_property_form',
                    self._get_property_form_values(None, errors=errors, values=values)
                )

        return request.render(
            'web_portal.portal_property_form',
            self._get_property_form_values(None, values={})
        )

    @http.route(['/my/properties/<int:property_id>/edit'], type='http', auth='user', website=True, csrf=True, methods=['GET', 'POST'])
    def portal_property_edit(self, property_id, **kw):
        property_rec = request.env['property'].browse(property_id)
        if not property_rec.exists() or property_rec.user_id.id != request.env.user.id:
            return request.redirect('/my/properties')

        if request.httprequest.method == 'POST':
            values = self._parse_property_form(kw)
            errors = self._validate_property_form(values)
            
            if errors:
                return request.render(
                    'web_portal.portal_property_form',
                    self._get_property_form_values(property_rec, errors=errors, values=values)
                )
            try:
                property_rec.write(values)
                return request.redirect('/my/properties/%s' % property_rec.id)
            except Exception as exc:
                request.env.cr.rollback()
                errors['form'] = str(exc)
                _logger.error("Portal edit property failed: %s", exc, exc_info=True)
                return request.render(
                    'web_portal.portal_property_form',
                    self._get_property_form_values(property_rec, errors=errors, values=values)
                )

        values = {
            'name': property_rec.name or '',
            'description': property_rec.description or '',
            'postcode': property_rec.postcode or '',
            'expected_price': property_rec.expected_price or 0.0,
            'bedrooms': property_rec.bedrooms or 0,
            'living_area': property_rec.living_area or 0,
            'facades': property_rec.facades or 0,
            'garage': bool(property_rec.garage),
            'garden': bool(property_rec.garden),
            'garden_area': property_rec.garden_area or 0,
            'garden_orientation': property_rec.garden_orientation or 'north',
            'expected_date_selling': property_rec.expected_date_selling or False,
        }
        return request.render(
            'web_portal.portal_property_form',
            self._get_property_form_values(property_rec, values=values)
        )

    @http.route(['/my/properties/xlsx_report'], type='http', auth='user', website=True)
    def portal_my_properties_xlsx_report(self, **kw):
        Property = request.env['property']
        domain = self._get_property_domain()
        search = (kw.get('search') or '').strip()
        if search:
            domain = domain + ['|', '|',
                               ('name', 'ilike', search),
                               ('ref', 'ilike', search),
                               ('state', 'ilike', search)]

        properties = Property.search(domain)
        property_ids = properties.ids
        export_window = timedelta(minutes=5)
        _logger.info(
            "Portal Excel export for user %s with %s properties (window: %s)",
            request.env.user.id,
            len(property_ids),
            export_window,
        )

        url = '/property/xlsx_report'
        if property_ids:
            url += '?property_ids=%s' % json.dumps(property_ids)
        return request.redirect(url)

    @http.route(['/my/properties/<int:property_id>'], type='http', auth='user', website=True)
    def portal_my_property(self, property_id, **kw):
        property_rec = request.env['property'].browse(property_id)

        if not property_rec.exists() or property_rec.user_id.id != request.env.user.id:
            return request.redirect('/my/properties')

        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'property',
            'property': property_rec,
            'breadcrumbs': [
                {'name': _('Properties'), 'url': '/my/properties'},
                {'name': property_rec.name, 'active': True},
            ],
        })
        return request.render('web_portal.portal_my_property', values)

    @http.route(['/my/properties/<int:property_id>/xlsx_report'], type='http', auth='user', website=True)
    def portal_my_property_xlsx_report(self, property_id, **kw):
        property_rec = request.env['property'].browse(property_id)

        if not property_rec.exists() or property_rec.user_id.id != request.env.user.id:
            return request.redirect('/my/properties')

        _logger.info(
            "Portal Excel export for property %s by user %s",
            property_rec.id,
            request.env.user.id,
        )

        url = '/property/xlsx_report?property_ids=%s' % json.dumps([property_rec.id])
        return request.redirect(url)

    @http.route(['/my/properties/<int:property_id>/report'], type='http', auth='user', website=True)
    def portal_property_report(self, property_id, **kw):
        property_rec = request.env['property'].browse(property_id)

        if not property_rec.exists() or property_rec.user_id.id != request.env.user.id:
            return request.redirect('/my/properties')

        report = request.env['ir.actions.report'].sudo()
        pdf_content, _ = report._render_qweb_pdf(
            'app_one.action_report_property',
            res_ids=[property_rec.id],
        )
        filename = 'Property-%s.pdf' % (property_rec.ref or property_rec.id)
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', 'attachment; filename="%s"' % filename),
        ]
        return request.make_response(pdf_content, headers=headers)
