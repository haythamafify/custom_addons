from odoo import models, fields

class HospitalMonthlyReport(models.Model):
    _name = 'hospital.monthly.report'
    _description = 'Hospital Monthly Report'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'name'

    report_month = fields.Date(string='Report Month', required=True)  # Field for the month of the report
    total_patients = fields.Integer(string='Total Patients', default=0)  # Total number of patients in the month
    total_appointments = fields.Integer(string='Total Appointments', default=0)  # Total number of appointments
    total_income = fields.Float(string='Total Income', default=0.0)  # Total income generated
    total_expenses = fields.Float(string='Total Expenses', default=0.0)  # Total expenses incurred
    most_common_disease = fields.Char(string='Most Common Disease', size=255)  # The most common disease in the hospital during the month
    notes = fields.Text(string='Notes')  # Additional notes for the report
