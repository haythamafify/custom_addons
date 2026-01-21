from odoo import models, fields

class OwlTodolist(models.Model):
    _name = "owl.todo.list"
    _description = "OWL Todo List"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Task Name", required=True, tracking=True)
    completed = fields.Boolean(string="Completed", default=False, tracking=True)
    color = fields.Char(string="Color", default="#00C897")
