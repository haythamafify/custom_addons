from odoo import models, fields

class Owner(models.Model):
    _name = "owner"
    _description = "Owner of a Property"

    name = fields.Char(required=True, string="Owner Name")
    phone = fields.Char(string="Phone Number")
    address = fields.Char(string="Address")

    # This establishes the reverse relationship with Property
    property_ids = fields.One2many('property', 'owner_id', string="Properties")

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'The name must be unique.')
    ]
