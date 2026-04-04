# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import _, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    """
    Inherit stock.move to block validation of outgoing moves when the
    available quantity at the source location is insufficient.

    Checks are skipped for products whose category has
    ``allow_negative_stock = True``.
    """

    _inherit = 'stock.move'

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_moves_to_check(self):
        """
        Return the subset of *self* that must be validated against
        available stock:
          - State must be 'assigned' or 'partially_available' (ready to go).
          - Source location must be an internal location
            (usage == 'internal').
          - The product's category must NOT have allow_negative_stock set.
        """
        return self.filtered(
            lambda m: m.state in ('assigned', 'partially_available')
            and m.location_id.usage == 'internal'
            and not m.product_id.categ_id.allow_negative_stock
        )

    def _compute_location_product_qty(self, moves):
        """
        Return a dict keyed by (location_id, product_id) → available qty
        using a single SQL query for best performance across many moves.

        :param moves: recordset of stock.move
        :returns: defaultdict(float)
        """
        if not moves:
            return defaultdict(float)

        location_ids = moves.location_id.ids
        product_ids = moves.product_id.ids

        # Use the ORM quant model so UoM conversions and multi-company
        # filters are already handled correctly.
        quants = self.env['stock.quant'].search([
            ('location_id', 'in', location_ids),
            ('product_id', 'in', product_ids),
        ])

        available = defaultdict(float)
        for quant in quants:
            key = (quant.location_id.id, quant.product_id.id)
            available[key] += quant.quantity - quant.reserved_quantity

        return available

    # ------------------------------------------------------------------
    # Validation guard
    # ------------------------------------------------------------------

    def _check_negative_stock(self):
        """
        Raise UserError (in Arabic) listing every move that would push
        the location balance below zero.

        Aggregates demand per (location, product) before comparing with
        available stock so that multiple moves for the same item are
        evaluated together (worst-case scenario check).
        """
        moves_to_check = self._get_moves_to_check()
        if not moves_to_check:
            return

        # ── Step 1: aggregate demanded qty per (location, product) ──────
        # We work in the product's default UoM via product_uom_qty which
        # is already converted to the product UoM by the ORM.
        demand = defaultdict(float)  # (location_id, product_id) → total demand
        move_map = defaultdict(list)  # (location_id, product_id) → [move, ...]

        for move in moves_to_check:
            key = (move.location_id.id, move.product_id.id)
            # product_qty is in the product's internal (default) UoM
            demand[key] += move.product_qty
            move_map[key].append(move)

        # ── Step 2: fetch available quantities in one shot ───────────────
        available = self._compute_location_product_qty(moves_to_check)

        # ── Step 3: detect violations and build readable error message ───
        errors = []
        for key, demanded_qty in demand.items():
            avail_qty = available.get(key, 0.0)
            if demanded_qty > avail_qty:
                sample_move = move_map[key][0]
                product_name = sample_move.product_id.display_name
                location_name = sample_move.location_id.display_name
                uom_name = sample_move.product_uom.name

                errors.append(
                    _(
                        'المنتج: %(product)s\n'
                        'الموقع: %(location)s\n'
                        'الكمية المتاحة: %(available).2f %(uom)s\n'
                        'الكمية المطلوبة: %(demanded).2f %(uom)s\n',
                        product=product_name,
                        location=location_name,
                        available=avail_qty,
                        demanded=demanded_qty,
                        uom=uom_name,
                    )
                )

        if errors:
            header = _(
                'لا يمكن إتمام العملية — الكمية غير كافية في المخزن '
                'للمنتجات التالية:\n\n'
            )
            raise UserError(header + '\n'.join(errors))

    # ------------------------------------------------------------------
    # Override _action_done
    # ------------------------------------------------------------------

    def _action_done(self, cancel_backorder=False):
        """
        Intercept the final validation step and enforce the
        no-negative-stock rule before delegating to the standard flow.
        """
        self._check_negative_stock()
        return super()._action_done(cancel_backorder=cancel_backorder)
