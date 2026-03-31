# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    skip_end_date_check = fields.Boolean(
        string="Skip End Date Check",
        default=False,
        copy=False,
        store=True,
    )

    def write(self, vals):
        res = super(HrContract, self).write(vals)

        # Post message for contracts saved without end date
        if 'skip_end_date_check' in vals and vals.get('skip_end_date_check'):
            for contract in self:
                if not contract.date_end:
                    contract.message_post(
                        body=_('This contract has been saved without an end date. The contract is now open-ended.'),
                        subject=_('Open-Ended Contract Alert'),
                        message_type='notification',
                    )

        return res

    @api.model_create_multi
    def create(self, vals_list):
        contracts = super(HrContract, self).create(vals_list)

        for contract in contracts:
            if not contract.date_end and contract.skip_end_date_check:
                contract.message_post(
                    body=_('A new contract was created without an end date.'),
                    subject=_('New Open-Ended Contract'),
                    message_type='notification',
                )

        return contracts