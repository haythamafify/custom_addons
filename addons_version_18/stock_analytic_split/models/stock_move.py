from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_distribution = fields.Json(
        string='Analytic Distribution',
        help='Analytic accounts distribution for this stock move line.',
    )

    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get('Percentage Analytic'),
    )

    def _create_analytic_lines_from_distribution(self):
        """Create analytic lines based on analytic_distribution after validation."""
        self.ensure_one()
        analytic_line_obj = self.env['account.analytic.line']
        distribution = self.analytic_distribution or {}

        if not distribution:
            return

        total_cost = self._compute_move_cost()
        if not total_cost:
            _logger.warning(
                'No cost for move %s (product: %s). Skipping analytic lines.',
                self.id, self.product_id.display_name,
            )
            return

        analytic_account_obj = self.env['account.analytic.account']

        for account_id_str, percentage in distribution.items():
            account = analytic_account_obj.browse(int(account_id_str))
            if not account.exists():
                continue

            analytic_line_obj.create({
                'name': '%s - %s' % (self.picking_id.name or '', self.product_id.display_name),
                'account_id': account.id,
                'amount': -(total_cost * percentage / 100.0),
                'date': (self.picking_id.date_done.date()
                         if self.picking_id and self.picking_id.date_done
                         else fields.Date.today()),
                'ref': self.picking_id.name if self.picking_id else '',
                'product_id': self.product_id.id,
                'unit_amount': self.quantity * percentage / 100.0,
                'product_uom_id': self.product_uom.id,
                'company_id': self.company_id.id,
            })

    def _compute_move_cost(self):
        """Get total cost. Uses valuation layers first, falls back to standard price."""
        self.ensure_one()
        cost = 0.0
        if hasattr(self, 'stock_valuation_layer_ids') and self.stock_valuation_layer_ids:
            cost = abs(sum(self.stock_valuation_layer_ids.mapped('value')))
        if not cost:
            cost = self.product_id.standard_price * self.quantity
        return cost
