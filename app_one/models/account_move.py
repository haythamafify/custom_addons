from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_do_some_thing(self):
        print(self, "some thing")
