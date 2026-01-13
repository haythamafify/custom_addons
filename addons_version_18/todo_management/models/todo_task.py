from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class TodoTask(models.Model):
    _name = "todo.task"
    _description = "Todo Task"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _log_access = True
    _order = 'priority desc, due_date asc, id desc'

    name = fields.Char(
        string="Task Title",
        required=True,
        tracking=True
    )

    assign_to = fields.Many2one(
        'res.users',
        string="Assigned To",
        tracking=True,
        default=lambda self: self.env.user
    )

    due_date = fields.Date(
        string="Due Date",
        tracking=True
    )

    state = fields.Selection(
        [
            ('new', 'New'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        string="Status",
        default='new',
        tracking=True,
        required=True
    )

    priority = fields.Selection(
        [
            ('0', 'Low'),
            ('1', 'Normal'),
            ('2', 'High'),
            ('3', 'Urgent'),
        ],
        string="Priority",
        default='1',
        tracking=True
    )

    description = fields.Text(
        string="Description",
        tracking=True,
        translate=True
    )

    tag_ids = fields.Many2many(
        'todo.task.tag',
        string="Tags",
        tracking=True
    )

    progress = fields.Float(
        string="Progress (%)",
        default=0.0,
        tracking=True
    )

    is_overdue = fields.Boolean(
        string="Is Overdue",
        compute='_compute_is_overdue',
        store=True
    )

    deadline_status = fields.Selection(
        [
            ('on_time', 'On Time'),
            ('due_soon', 'Due Soon'),
            ('overdue', 'Overdue'),
        ],
        string="Deadline Status",
        compute='_compute_deadline_status',
        store=True
    )

    completed_date = fields.Datetime(
        string="Completed Date",
        readonly=True,
        tracking=True
    )

    notes = fields.Html(
        string="Additional Notes"
    )

    attachment_count = fields.Integer(
        string="Attachments",
        compute='_compute_attachment_count'
    )

    @api.depends('due_date', 'state')
    def _compute_is_overdue(self):
        today = date.today()
        for task in self:
            if task.due_date and task.state not in ['completed', 'cancelled']:
                task.is_overdue = task.due_date < today
            else:
                task.is_overdue = False

    @api.depends('due_date', 'state')
    def _compute_deadline_status(self):
        today = date.today()
        for task in self:
            if not task.due_date or task.state in ['completed', 'cancelled']:
                task.deadline_status = 'on_time'
            elif task.due_date < today:
                task.deadline_status = 'overdue'
            elif (task.due_date - today).days <= 3:
                task.deadline_status = 'due_soon'
            else:
                task.deadline_status = 'on_time'

    def _compute_attachment_count(self):
        for task in self:
            task.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'todo.task'),
                ('res_id', '=', task.id)
            ])

    @api.constrains('progress')
    def _check_progress(self):
        for task in self:
            if task.progress < 0 or task.progress > 100:
                raise ValidationError(_("Progress must be between 0 and 100%"))

    @api.constrains('due_date')
    def _check_due_date(self):
        for task in self:
            if task.due_date and task.due_date < date.today() and task.state == 'new':
                raise ValidationError(_("Due date cannot be in the past for new tasks"))

    def action_start(self):
        """Start working on task"""
        self.write({
            'state': 'in_progress',
            'progress': 10.0 if self.progress == 0 else self.progress
        })
        self.message_post(body=_("Task started"))

    def action_complete(self):
        """Mark task as completed"""
        self.write({
            'state': 'completed',
            'progress': 100.0,
            'completed_date': fields.Datetime.now()
        })
        self.message_post(body=_("Task completed! 🎉"))

    def action_cancel(self):
        """Cancel task"""
        self.write({'state': 'cancelled'})
        self.message_post(body=_("Task cancelled"))

    def action_reset_to_new(self):
        """Reset task to new state"""
        self.write({
            'state': 'new',
            'progress': 0.0,
            'completed_date': False
        })
        self.message_post(body=_("Task reset to new"))

    def action_view_attachments(self):
        """View task attachments"""
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [('res_model', '=', 'todo.task'), ('res_id', '=', self.id)],
            'context': {
                'default_res_model': 'todo.task',
                'default_res_id': self.id
            }
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Send notification when task is created"""
        tasks = super(TodoTask, self).create(vals_list)
        for task in tasks:
            if task.assign_to:
                task.message_subscribe(partner_ids=[task.assign_to.partner_id.id])
                task.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=task.assign_to.id,
                    summary=_('New task assigned: %s') % task.name,
                    date_deadline=task.due_date or date.today()
                )
        return tasks

    def write(self, vals):
        """Notify assignee when task is reassigned"""
        old_assignee = self.assign_to
        res = super(TodoTask, self).write(vals)

        if 'assign_to' in vals and vals.get('assign_to') != old_assignee.id:
            new_assignee = self.env['res.users'].browse(vals['assign_to'])
            if new_assignee:
                self.message_subscribe(partner_ids=[new_assignee.partner_id.id])
                self.message_post(
                    body=_('Task reassigned to %s') % new_assignee.name,
                    partner_ids=[new_assignee.partner_id.id]
                )

        return res


class TodoTaskTag(models.Model):
    _name = "todo.task.tag"
    _description = "Task Tag"

    name = fields.Char(
        string="Tag Name",
        required=True,
        translate=True
    )

    color = fields.Integer(
        string="Color Index"
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Tag name already exists!')
    ]