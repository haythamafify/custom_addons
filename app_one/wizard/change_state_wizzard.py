from odoo import models, fields


class ChangeState(models.TransientModel):
    _name = "change.state"
    _description = "change property state"

    property_id = fields.Many2one('property')
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), ('sold', 'Sold'), ('closed', 'Closed'), ],
                             default='draft')
    reason = fields.Char()

    def action_confirm(self):
        if self.property_id.state == 'closed':
            self.property_id.state = self.state
            self.property_id.create_history_record('closed', self.state, self.reason)
