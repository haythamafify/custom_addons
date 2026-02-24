from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse",
        relation="res_users_stock_warehouse_rel",
        column1="user_id",
        column2="warehouse_id",
        string="Allowed Warehouses",
        help="Warehouses this user is allowed to access.",
    )
