from odoo import fields, models


class TodoTask(models.Model):
    _name = "todo.task"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Task for To-Do App"

    # Task Name
    task_name = fields.Char(string="Task Name", required=True)

    # Assigned User (Many2one relationship with res.users)
    user = fields.Many2one("res.users", string="Assigned User")  # Link to users, or keep it as "res.partner"

    # Task Description
    description = fields.Text(string="Description")

    # Due Date for the task
    due_date = fields.Datetime(string="Due Date")

    # Status of the Task (New, In Progress, Completed)
    status = fields.Selection(
        [('new', 'New'), ('inprogress', 'In Progress'), ('completed', 'Completed'), ('on_hold', 'On Hold')],
        string="Status",
        default='new'
    )

    # Optional: Related field to display User's Name in the task form view
    user_name = fields.Char(related="user.name", string="User Name", store=True)

    # Optional: Adding default description or computed field logic
    default_description = fields.Text(string="Default Description", default="This is a default task description")
