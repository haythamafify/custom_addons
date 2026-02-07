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
