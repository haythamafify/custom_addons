from odoo import models, fields, api

class HrLeaveInherit(models.Model):
    _inherit = 'hr.leave'

    # إضافة حقل جديد لسبب الإجازة
    leave_reason = fields.Char(string='Reason for Time Off')
