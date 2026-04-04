# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    allow_negative_stock = fields.Boolean(
        string='Allow Negative Stock',
        default=False,
        help=(
            'If enabled, products in this category are allowed to have '
            'negative stock quantities. When disabled (default), the system '
            'will block any stock move that would result in a negative balance.'
        ),
    )
