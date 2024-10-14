
from odoo import models,fields,api

class University(models.Model):
    _name = 'education.university'
    _description = 'university'

    name = fields.Char(string='اسم الجامعة', required=True)


    _sql_constraints = [
        ('name_unique', 'unique(name)', 'اسم الجامعة يجب أن يكون فريدًا!')
    ]
