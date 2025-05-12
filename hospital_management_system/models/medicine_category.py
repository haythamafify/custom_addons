from odoo import models, fields


class MedicineCategory(models.Model):
    _name = 'hospital.medicine.category'
    _description = 'Medicine Category'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _log_access = True

    name = fields.Char(string="Category Name", required=True)
    description = fields.Text(string="Description")
