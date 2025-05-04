import re
from datetime import date

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HREmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee Extension'

    code = fields.Char(string='كود الموظف', required=True)
    contract_type = fields.Selection([
        ('temporary', 'مؤقت'),
        ('seconded', 'منتدب'),
        ('on_loan', 'معار'),
        ('permanent', 'دائم'),
    ], string='نوع التعاقد', required=True)
    # حقل لتحديد تصنيف الموظف، هل هو إداري أم عضو هيئة تدريس
    employee_category = fields.Selection([
        ('admin', 'إداري'),
        ('faculty', 'عضو هيئة تدريس')
    ], string="تصنيف الموظف", required=True)

    hiring_date = fields.Date(string='تاريخ التعيين')
    insurance_number = fields.Char(string='الرقم التأميني', size=10)
    insurance_date = fields.Date(string='تاريخ التأمين')
    insurance_status = fields.Selection(
        [
            ('insured', 'مؤمن عليه'),
            ('seconded', 'معار'),
            ('not_insured', 'غير مؤمن'),
            ('insured_other', 'مؤمن جهة أخرى')
        ],
        string='الموقف التأميني',
        required=True,
        default='not_insured'
    )
    birth_date = fields.Date(string='تاريخ الميلاد', required=True)
    national_id = fields.Char(string='الرقم القومي', required=True, size=14)
    national_id_expiry_date = fields.Date(string='تاريخ انتهاء الرقم القومي')

    gender = fields.Selection(selection_add=[
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ], string='النوع', required=True)

    marital_status = fields.Selection([
        ('single', 'أعزب'),
        ('married', 'متزوج'),
        ('divorced', 'مطلق'),
        ('widowed', 'أرمل'),
    ], string='الحالة الاجتماعية', required=True)

    # حساب مدة الخدمة
    service_duration = fields.Integer(string='مدة الخدمة (بالسنوات)', compute='_compute_service_duration', store=True)

    loan_start_date = fields.Date(string='تاريخ بداية الإعارة')
    loan_end_date = fields.Date(string='تاريخ نهاية الإعارة')
    work_place = fields.Char(string='جهة العمل')

    other_job_leave_start = fields.Date(string='تاريخ بداية الإجازة من جهة العمل الأخرى')
    other_job_leave_end = fields.Date(string='تاريخ نهاية الإجازة من جهة العمل الأخرى')
    leave_start_date = fields.Date(string='تاريخ بداية الإجازة بدون مرتب')
    leave_end_date = fields.Date(string='تاريخ نهاية الإجازة بدون مرتب')
    leave_duration = fields.Integer(string='مدة الإجازة بدون مرتب', compute='_compute_leave_duration')

    military_status = fields.Selection([
        ('exempted', 'معفي'),
        ('completed', 'مكتمل'),
        ('pending', 'مؤجل'),
        ('not_completed', 'غير مكتمل'),
    ], string='الموقف من التجنيد')
    military_expiry_date = fields.Date(string='تاريخ انتهاء التجنيد')

    education_level = fields.Selection([
        ('none', 'لا يوجد'),
        ('literacy', 'محو الأمية'),
        ('primary', 'ابتدائية'),
        ('intermediate', 'إعدادية'),
        ('high_school', 'ثانوية عامة'),
        ('bachelor', 'بكالوريوس'),
        ('master', 'ماجستير'),
        ('phd', 'دكتوراه'),
    ], string='المؤهل الدراسي')

    university_ids = fields.Many2many('education.university', string='الجامعات')
    master_degree = fields.Char(string='درجة الماجستير')
    master_degree_date = fields.Date(string='تاريخ الحصول على الماجستير')
    phd_degree = fields.Char(string='درجة الدكتوراه')
    phd_degree_date = fields.Date(string='تاريخ الحصول على الدكتوراه')
    assistant_professor_degree = fields.Char(string='درجة الأستاذ المساعد')
    assistant_professor_date = fields.Date(string='تاريخ الحصول على درجة الأستاذ المساعد')
    professor_degree = fields.Char(string='درجة الأستاذ')
    professor_date = fields.Date(string='تاريخ الحصول على درجة الأستاذ')

    qualification_duration = fields.Integer(string='المدة القانونية للمؤهل (بالسنوات)')

    health_status = fields.Selection([
        ('healthy', 'سليم'),
        ('sick', 'مريض'),
        ('chronic', 'مزمن'),
        ('other', 'أخرى')
    ], string='الحالة الصحية')

    id_card_image = fields.Binary(string='صورة البطاقة')
    annual_activity_score = fields.Float(string='درجة النشاط السنوي')
    notes = fields.Text(string='ملاحظات')

    # حساب مدة الخدمة
    @api.depends('hiring_date')
    def _compute_service_duration(self):
        for record in self:
            if record.hiring_date:
                today = date.today()
                hiring_date = fields.Date.from_string(record.hiring_date)
                record.service_duration = today.year - hiring_date.year - (
                        (today.month, today.day) < (hiring_date.month, hiring_date.day))
            else:
                record.service_duration = 0

    # حساب مدة الإجازة
    @api.depends('leave_start_date', 'leave_end_date')
    def _compute_leave_duration(self):
        for record in self:
            if record.leave_start_date and record.leave_end_date:
                start = fields.Date.from_string(record.leave_start_date)
                end = fields.Date.from_string(record.leave_end_date)
                record.leave_duration = (end - start).days + 1
            else:
                record.leave_duration = 0

    # التحقق من رقم التأمين
    @api.constrains('insurance_number')
    def _check_insurance_number(self):
        for record in self:
            if record.insurance_number and not re.match(r'^\d{1,10}$', record.insurance_number):
                raise ValidationError("الرقم التأميني يجب أن يتكون من 1 إلى 10 أرقام.")

    # التحقق من الرقم القومي
    @api.constrains('national_id')
    def _check_national_id(self):
        for record in self:
            if not re.match(r'^\d{14}$', record.national_id):
                raise ValidationError("الرقم القومي يجب أن يتكون من 14 رقمًا.")

    # التحقق من تواريخ الإجازة
    @api.constrains('leave_start_date', 'leave_end_date')
    def _check_leave_dates(self):
        for record in self:
            if record.leave_start_date and record.leave_end_date:
                if record.leave_end_date < record.leave_start_date:
                    raise ValidationError("تاريخ نهاية الإجازة يجب أن يكون بعد تاريخ البداية.")

    # التحقق من تاريخ التعيين
    @api.constrains('hiring_date')
    def _check_hiring_date(self):
        for record in self:
            if record.hiring_date and record.hiring_date > date.today():
                raise ValidationError("تاريخ التعيين لا يمكن أن يكون في المستقبل.")

    # التحقق من تاريخ الميلاد
    @api.constrains('birth_date')
    def _check_birth_date(self):
        for record in self:
            if record.birth_date and record.birth_date > date.today():
                raise ValidationError("تاريخ الميلاد لا يمكن أن يكون في المستقبل.")

    # التحقق من المدة القانونية للمؤهل
    @api.constrains('qualification_duration')
    def _check_qualification_duration(self):
        for record in self:
            if record.qualification_duration < 0:
                raise ValidationError("المدة القانونية للمؤهل يجب أن تكون رقمًا غير سالب.")
