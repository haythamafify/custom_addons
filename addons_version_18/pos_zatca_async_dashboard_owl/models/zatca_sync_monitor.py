from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class ZatcaSyncMonitor(models.Model):
    _name = 'zatca.sync.monitor'
    _description = 'ZATCA Sync Monitor'
    _rec_name = 'company_id'
    _order = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )

    date_today = fields.Date(
        string='Today',
        compute='_compute_date_today',
    )
    pending_today_count = fields.Integer(
        string='Pending Today',
        compute='_compute_stats',
    )
    sent_today_count = fields.Integer(
        string='Sent Today',
        compute='_compute_stats',
    )
    error_today_count = fields.Integer(
        string='Error Today',
        compute='_compute_stats',
    )

    move_ids = fields.Many2many(
        'account.move',
        string='Pending / Error Invoices',
        compute='_compute_move_ids',
    )

    @api.depends()
    def _compute_date_today(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.date_today = today

    def _domain_base_moves(self, company):
        return [
            ('company_id', '=', company.id),
            ('state', '=', 'posted'),
            ('move_type', 'in', ('out_invoice', 'out_refund')),
        ]

    def _domain_today(self):
        today = fields.Date.context_today(self)
        # Prefer invoice_date when set; fallback to accounting date.
        return [
            '|',
            ('invoice_date', '=', today),
            '&',
            ('invoice_date', '=', False),
            ('date', '=', today),
        ]

    def _sent_states(self):
        # Keep it resilient across l10n_sa_edi versions.
        return ('sent', 'accepted', 'cleared', 'done')

    def _get_state_field(self):
        return self.env['account.move']._get_zatca_edi_state_field_name()

    @api.depends('company_id')
    def _compute_stats(self):
        Move = self.env['account.move']
        today_domain = self._domain_today()
        for rec in self:
            state_field = rec._get_state_field()
            if not state_field:
                _logger.warning(
                    "ZATCA sync monitor: could not find ZATCA EDI state field on account.move. "
                    "Stats will be 0."
                )
                rec.pending_today_count = 0
                rec.sent_today_count = 0
                rec.error_today_count = 0
                continue

            base = rec._domain_base_moves(rec.company_id)

            rec.pending_today_count = Move.search_count(
                base + today_domain + [(state_field, '=', 'to_send')]
            )
            rec.sent_today_count = Move.search_count(
                base + today_domain + [(state_field, 'in', rec._sent_states())]
            )
            rec.error_today_count = Move.search_count(
                base + today_domain + [(state_field, '=', 'error')]
            )

    @api.depends('company_id')
    def _compute_move_ids(self):
        Move = self.env['account.move']
        for rec in self:
            state_field = rec._get_state_field()
            if not state_field:
                rec.move_ids = Move.browse()
                continue

            domain = rec._domain_base_moves(rec.company_id) + [
                (state_field, 'in', ('to_send', 'error')),
            ]
            rec.move_ids = Move.search(domain, order='invoice_date asc, id asc')

    def action_force_run_cron(self):
        cron = self.env.ref('pos_zatca_async_dashboard_owl.ir_cron_zatca_async', raise_if_not_found=False)
        if not cron:
            raise UserError(_('Cron record not found.'))
        cron.sudo().method_direct_trigger()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('ZATCA Cron Triggered'),
                'message': _('The ZATCA async cron was triggered successfully.'),
                'sticky': False,
            }
        }

    def _action_open_moves(self, domain, name):
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {
                'default_move_type': 'out_invoice',
            },
        }

    def action_open_today_pending(self):
        self.ensure_one()
        state_field = self._get_state_field()
        if not state_field:
            raise UserError(_("ZATCA EDI state field is not available on invoices in this database."))
        domain = self._domain_base_moves(self.company_id) + self._domain_today() + [
            (state_field, '=', 'to_send'),
        ]
        return self._action_open_moves(domain, _('Pending Today'))

    def action_open_today_sent(self):
        self.ensure_one()
        state_field = self._get_state_field()
        if not state_field:
            raise UserError(_("ZATCA EDI state field is not available on invoices in this database."))
        domain = self._domain_base_moves(self.company_id) + self._domain_today() + [
            (state_field, 'in', self._sent_states()),
        ]
        return self._action_open_moves(domain, _('Sent Today'))

    def action_open_today_error(self):
        self.ensure_one()
        state_field = self._get_state_field()
        if not state_field:
            raise UserError(_("ZATCA EDI state field is not available on invoices in this database."))
        domain = self._domain_base_moves(self.company_id) + self._domain_today() + [
            (state_field, '=', 'error'),
        ]
        return self._action_open_moves(domain, _('Errors Today'))
