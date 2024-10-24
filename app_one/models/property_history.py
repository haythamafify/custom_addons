from odoo import models, fields, api



class Property(models.Model):
    _name = "property.history"
    _description = "Property History"


    user_id = fields.Many2one('res.users')
    property_id = fields.Many2one('property')
    old_state = fields.Char()
    new_state = fields.Char()
