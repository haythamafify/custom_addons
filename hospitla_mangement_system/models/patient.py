# -*- coding: utf-8 -*-

import re
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Patient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # الحقول
    name = fields.Char(string='Name', required=True, tracking=True)
    date_of_birth = fields.Date(string='Date of Birth', tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True, tracking=True)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                today = datetime.today().date()  # تأكد من استخدام .date() للحصول على التاريخ فقط
                birth_date = fields.Date.from_string(rec.date_of_birth)  # هذا سيعيد كائن من نوع date

                # الآن يمكننا إجراء الطرح بشكل صحيح
                delta = today - birth_date

                # حساب العمر بالسنوات
                years = today.year - birth_date.year

                # إذا لم تمر هذه السنة بعد (اليوم والشهر أقل من تاريخ الميلاد)
                if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                    years -= 1

                # حساب الأشهر المتبقية
                months = today.month - birth_date.month
                if today.day < birth_date.day:
                    months -= 1

                if months < 0:
                    months += 12

                # حساب الأيام المتبقية
                if today.day < birth_date.day:
                    days = (today.replace(year=today.year, month=today.month) - birth_date).days
                else:
                    days = today.day - birth_date.day

                # إرجاع العمر بالتنسيق الذي تريده
                rec.age = years  # العمر بالسنوات فقط
                # أو إذا أردت عرض العمر كاملًا:
                # rec.age = f"{years} years, {months} months, {days} days"

            else:
                rec.age = 0

    @api.constrains('age')
    def _check_age(self):
        for rec in self:
            if rec.age < 18:
                raise ValidationError("Patient must be 18 or older.")

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', tracking=True)
    phone = fields.Char(string='Phone', required=True)

    email = fields.Char(string='Email')

    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email and not re.match(r"[^@]+@[^@]+\.[^@]+", rec.email):
                raise ValidationError("Please enter a valid email address.")

    blood_type = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-')
    ], string='Blood Type')
    notes = fields.Text(string='Notes')

    # التأكد من فريدية الإيميل والهاتف
    _sql_constraints = [
        ('unique_email', 'UNIQUE(email)', 'Email must be unique!'),
        ('unique_phone', 'UNIQUE(phone)', 'Phone must be unique!')
    ]
