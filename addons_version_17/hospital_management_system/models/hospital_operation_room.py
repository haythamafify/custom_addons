from odoo import models, fields

class HospitalOperationRoom(models.Model):
    _name = 'hospital.operation.room'
    _description = 'Hospital Operation Room'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'


    name = fields.Char(string="Room Name", required=True)
    equipment = fields.Text(string="Available Equipment")
    is_available = fields.Boolean(string="Is Available", default=True)
    room_type = fields.Selection([
        ('general', 'General'),
        ('icu', 'ICU'),
        ('emergency', 'Emergency'),
        ('surgery', 'Surgery'),
    ], string="Room Type", required=True)
    notes = fields.Text(string="Notes")
