from odoo import fields, models


class TodoTask(models.Model):
    _name = "todo.task"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Task for To-Do App"  # display name for user

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
    active = fields.Boolean(default=True)

    # Optional: Related field to display User's Name in the task form view
    user_name = fields.Char(related="user.name", string="User Name", store=True)
    estimate_time = fields.Float(string="Estimated Time (in hours)",
                                 help="Estimated time to complete the task in hours")

    def action_new(self):
        for rec in self:
            rec.status = 'new'

    def action_inprogress(self):
        for rec in self:
            rec.status = 'inprogress'

    def action_completed(self):
        for rec in self:
            rec.status = 'completed'

    def action_on_hold(self):
        for rec in self:
            rec.status = 'on_hold'
