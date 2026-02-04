# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class PropertyPortal(CustomerPortal):

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

        property_count = Property.search_count(domain)
        pager = portal_pager(
            url='/my/properties',
            total=property_count,
            page=page,
            step=self._items_per_page
        )

        properties = Property.search(
            domain,
            order='create_date desc',
            limit=self._items_per_page,
            offset=pager['offset']
        )

        values.update({
            'page_name': 'properties',
            'properties': properties,
            'pager': pager,
            'default_url': '/my/properties',
        })
        return request.render('web_portal.portal_my_properties', values)

    @http.route(['/my/properties/<int:property_id>'], type='http', auth='user', website=True)
    def portal_my_property(self, property_id, **kw):
        property_rec = request.env['property'].browse(property_id)

        if not property_rec.exists() or property_rec.user_id.id != request.env.user.id:
            return request.redirect('/my/properties')

        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'property',
            'property': property_rec,
        })
        return request.render('web_portal.portal_my_property', values)
