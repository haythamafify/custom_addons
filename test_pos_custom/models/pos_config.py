from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = "pos.config"
    default_payment_method = fields.Many2one(
        "pos.payment.method",
        string="طريقة الدفع الافتراضية",
        help="ستُستخدم هذه الطريقة للدفع كطريقة افتراضية للجلسات الجديدة."
    )
