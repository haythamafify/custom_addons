from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Owner(models.Model):
    _name = "owner"
    _description = 'Property Owner'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Fields
    name = fields.Char(string='Owner Name', required=True)
    phone = fields.Char(string='Phone')
    address = fields.Char(string='Address')

    # ✅ الحقل المهم - ربط المالك بـ Contact
    partner_id = fields.Many2one(
        'res.partner',
        string='Related Contact',
        ondelete='restrict',
        help="Link this owner to a customer/vendor in the system"
    )

    # Relations
    property_ids = fields.One2many('property', 'owner_id', string="Properties")

    # Computed Fields
    property_count = fields.Integer(
        compute='_compute_property_count',
        string='Properties'
    )

    @api.depends('property_ids')
    def _compute_property_count(self):
        """حساب عدد العقارات المملوكة"""
        for record in self:
            record.property_count = len(record.property_ids)

    def action_view_properties(self):
        """عرض كل العقارات المملوكة"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Properties of %s', self.name),
            'res_model': 'property',
            'view_mode': 'list,form',
            'domain': [('owner_id', '=', self.id)],
            'context': {
                'default_owner_id': self.id,
            },
        }

    _sql_constraints = [
        ('unique_owner_name', 'unique(lower(name))', 'Owner name already exists')
    ]