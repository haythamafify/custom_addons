# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PropertyChangeWizard(models.TransientModel):
    """
    معالج لتسجيل التغييرات على العقارات مع توثيق السبب
    Wizard for tracking property changes with reason documentation
    """
    _name = 'property.change.wizard'
    _description = 'Property Change Wizard'

    # العقار المراد تعديله
    property_id = fields.Many2one(
        'property',
        string='Property',
        required=True,
        readonly=True
    )

    # السبب - حقل إجباري
    reason = fields.Text(
        string='Reason for Change',
        required=True,
        help='Please explain why you are making these changes'
    )

    # ========== تغيير الحالة ==========
    change_state = fields.Boolean(string='Change State')
    current_state = fields.Selection(
        related='property_id.state',
        string='Current State',
        readonly=True
    )
    new_state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('closed', 'Closed')
    ], string='New State')

    # ========== تغيير الأسعار ==========
    change_price = fields.Boolean(string='Change Pricing')
    current_expected_price = fields.Float(
        related='property_id.expected_price',
        string='Current Expected Price',
        readonly=True
    )
    new_expected_price = fields.Float(string='New Expected Price')

    current_selling_price = fields.Float(
        related='property_id.selling_price',
        string='Current Selling Price',
        readonly=True
    )
    new_selling_price = fields.Float(string='New Selling Price')

    # ========== تغيير المالك والمسؤول ==========
    change_owner = fields.Boolean(string='Change Owner/Responsible')
    current_owner = fields.Many2one(
        related='property_id.owner_id',
        string='Current Owner',
        readonly=True
    )
    new_owner_id = fields.Many2one('owner', string='New Owner')

    current_user = fields.Many2one(
        related='property_id.user_id',
        string='Current Responsible',
        readonly=True
    )
    new_user_id = fields.Many2one('res.users', string='New Responsible')

    # ========== تغيير التواريخ ==========
    change_dates = fields.Boolean(string='Change Dates')
    current_date_availability = fields.Date(
        related='property_id.date_availability',
        string='Current Availability Date',
        readonly=True
    )
    new_date_availability = fields.Date(string='New Availability Date')

    current_expected_date_selling = fields.Date(
        related='property_id.expected_date_selling',
        string='Current Expected Selling Date',
        readonly=True
    )
    new_expected_date_selling = fields.Date(string='New Expected Selling Date')

    # ========== تغيير تفاصيل العقار ==========
    change_details = fields.Boolean(string='Change Property Details')
    current_bedrooms = fields.Integer(
        related='property_id.bedrooms',
        string='Current Bedrooms',
        readonly=True
    )
    new_bedrooms = fields.Integer(string='New Bedrooms', default=1)

    current_living_area = fields.Integer(
        related='property_id.living_area',
        string='Current Living Area',
        readonly=True
    )
    new_living_area = fields.Integer(string='New Living Area (sqm)')

    current_facades = fields.Integer(
        related='property_id.facades',
        string='Current Facades',
        readonly=True
    )
    new_facades = fields.Integer(string='New Facades')

    current_garage = fields.Boolean(
        related='property_id.garage',
        string='Current Garage',
        readonly=True
    )
    new_garage = fields.Boolean(string='New Garage')

    current_garden = fields.Boolean(
        related='property_id.garden',
        string='Current Garden',
        readonly=True
    )
    new_garden = fields.Boolean(string='New Garden')

    current_garden_area = fields.Integer(
        related='property_id.garden_area',
        string='Current Garden Area',
        readonly=True
    )
    new_garden_area = fields.Integer(string='New Garden Area (sqm)')

    @api.constrains('new_expected_price', 'new_selling_price', 'new_bedrooms', 'new_living_area', 'new_facades',
                    'new_garden_area')
    def _check_values(self):
        """التحقق من صحة القيم"""
        for record in self:
            if record.change_price:
                if record.new_expected_price is not None and record.new_expected_price < 0:
                    raise UserError(_('Expected price cannot be negative!'))
                if record.new_selling_price is not None and record.new_selling_price < 0:
                    raise UserError(_('Selling price cannot be negative!'))

            if record.change_details:
                if record.new_bedrooms and record.new_bedrooms <= 0:
                    raise UserError(_('Bedrooms must be greater than zero!'))
                if record.new_living_area is not None and record.new_living_area < 0:
                    raise UserError(_('Living area cannot be negative!'))
                if record.new_facades is not None and record.new_facades < 0:
                    raise UserError(_('Facades cannot be negative!'))
                if record.new_garden_area is not None and record.new_garden_area < 0:
                    raise UserError(_('Garden area cannot be negative!'))

    def _format_history_value(self, field_name, value):
        """تنسيق القيمة للعرض في History"""
        if value is None:
            return 'Empty'

        # Handle Boolean fields
        if field_name in ['garage', 'garden']:
            return 'Yes' if value else 'No'

        # Handle Many2one fields
        if field_name in ['owner_id', 'user_id']:
            if isinstance(value, int):
                model_name = 'owner' if field_name == 'owner_id' else 'res.users'
                record = self.env[model_name].browse(value)
                return record.name if record.exists() else 'Deleted Record'
            return getattr(value, 'name', 'Empty')

        # Handle Selection fields
        if field_name == 'state':
            return dict(self._fields['new_state'].selection).get(value, str(value))

        # Handle Date fields
        if field_name in ['date_availability', 'expected_date_selling']:
            return value.strftime('%Y-%m-%d') if value else 'Empty'

        # Handle numeric fields
        if field_name in ['expected_price', 'selling_price']:
            return f"{value:,.2f}" if value else '0.00'

        return str(value) if value not in [False, ''] else 'Empty'

    def action_apply_changes(self):
        """
        تطبيق التغييرات على العقار مع تسجيل السبب
        Apply changes to property with reason logging
        """
        self.ensure_one()

        # التحقق من اختيار حقل واحد على الأقل
        if not any([
            self.change_state,
            self.change_price,
            self.change_owner,
            self.change_dates,
            self.change_details
        ]):
            raise UserError(_('Please select at least one field to change!'))

        # بناء قاموس التحديثات
        vals = {}
        changes = []

        # ========== تغيير الحالة ==========
        if self.change_state and self.new_state and self.new_state != self.current_state:
            vals['state'] = self.new_state
            state_labels = dict(self._fields['new_state'].selection)
            old_label = state_labels.get(self.current_state, self.current_state)
            new_label = state_labels.get(self.new_state, self.new_state)
            changes.append(f"State: {old_label} → {new_label}")

        # تغيير الأسعار
        if self.change_price:
            if self.new_expected_price is not None and self.new_expected_price != self.current_expected_price:
                vals['expected_price'] = self.new_expected_price
                changes.append(f"Expected Price: {self.current_expected_price:,.2f} → {self.new_expected_price:,.2f}")

            if self.new_selling_price is not None and self.new_selling_price != self.current_selling_price:
                vals['selling_price'] = self.new_selling_price
                changes.append(f"Selling Price: {self.current_selling_price:,.2f} → {self.new_selling_price:,.2f}")

        # تغيير المالك والمسؤول
        if self.change_owner:
            if self.new_owner_id and self.new_owner_id != self.current_owner:
                vals['owner_id'] = self.new_owner_id.id
                old_owner = self.current_owner.name if self.current_owner else 'None'
                changes.append(f"Owner: {old_owner} → {self.new_owner_id.name}")

            if self.new_user_id and self.new_user_id != self.current_user:
                vals['user_id'] = self.new_user_id.id
                old_user = self.current_user.name if self.current_user else 'None'
                changes.append(f"Responsible: {old_user} → {self.new_user_id.name}")

        # تغيير التواريخ
        if self.change_dates:
            if self.new_date_availability and self.new_date_availability != self.current_date_availability:
                vals['date_availability'] = self.new_date_availability
                changes.append(f"Availability Date: {self.current_date_availability} → {self.new_date_availability}")

            if self.new_expected_date_selling and self.new_expected_date_selling != self.current_expected_date_selling:
                vals['expected_date_selling'] = self.new_expected_date_selling
                changes.append(
                    f"Expected Selling Date: {self.current_expected_date_selling} → {self.new_expected_date_selling}")

        # تغيير التفاصيل
        if self.change_details:
            if self.new_bedrooms and self.new_bedrooms != self.current_bedrooms:
                vals['bedrooms'] = self.new_bedrooms
                changes.append(f"Bedrooms: {self.current_bedrooms} → {self.new_bedrooms}")

            if self.new_living_area is not None and self.new_living_area != self.current_living_area:
                vals['living_area'] = self.new_living_area
                changes.append(f"Living Area: {self.current_living_area} → {self.new_living_area} sqm")

            if self.new_facades is not None and self.new_facades != self.current_facades:
                vals['facades'] = self.new_facades
                changes.append(f"Facades: {self.current_facades} → {self.new_facades}")

            if self.new_garage != self.current_garage:
                vals['garage'] = self.new_garage
                changes.append(
                    f"Garage: {'Yes' if self.current_garage else 'No'} → {'Yes' if self.new_garage else 'No'}")

            if self.new_garden != self.current_garden:
                vals['garden'] = self.new_garden
                changes.append(
                    f"Garden: {'Yes' if self.current_garden else 'No'} → {'Yes' if self.new_garden else 'No'}")

                # إذا تم إلغاء Garden، قم بتصفير المساحة
                if not self.new_garden:
                    vals['garden_area'] = 0

            if self.new_garden_area is not None and self.new_garden_area != self.current_garden_area:
                vals['garden_area'] = self.new_garden_area
                changes.append(f"Garden Area: {self.current_garden_area} → {self.new_garden_area} sqm")

        # التحقق من وجود تغييرات فعلية
        if not vals:
            raise UserError(_('No actual changes detected. Please modify at least one value.'))

        _logger.info(f"WIZARD: Applying changes with reason: {self.reason}")
        _logger.info(f"WIZARD: Changes to apply: {vals}")

        # حفظ القيم القديمة قبل التطبيق
        old_values = {}
        for field_name in vals.keys():
            old_values[field_name] = self.property_id[field_name]

        # تطبيق التغييرات مع context خاص لمنع إنشاء History مكرر
        self.property_id.with_context(skip_history=True).write(vals)

        # إنشاء سجلات History يدوياً مع السبب
        history_fields = {
            'state': ('State', 'state_change'),
            'expected_price': ('Expected Price', 'price_change'),
            'selling_price': ('Selling Price', 'price_change'),
            'owner_id': ('Owner', 'owner_change'),
            'user_id': ('Responsible', 'write'),
            'date_availability': ('Available From', 'write'),
            'expected_date_selling': ('Expected Selling Date', 'write'),
            'bedrooms': ('Bedrooms', 'write'),
            'living_area': ('Living Area', 'write'),
            'facades': ('Facades', 'write'),
            'garage': ('Garage', 'write'),
            'garden': ('Garden', 'write'),
            'garden_area': ('Garden Area', 'write'),
        }

        for field_name in vals.keys():
            if field_name in history_fields:
                field_label, change_type = history_fields[field_name]
                old_value = self._format_history_value(field_name, old_values[field_name])
                new_value = self._format_history_value(field_name, vals[field_name])

                if old_value != new_value:
                    history_vals = {
                        'property_id': self.property_id.id,
                        'property_ref': self.property_id.ref,
                        'change_type': change_type,
                        'field_name': field_name,
                        'field_label': field_label,
                        'old_value': old_value,
                        'new_value': new_value,
                        'note': f'Field "{field_label}" changed from "{old_value}" to "{new_value}"',
                        'reason': self.reason
                    }

                    history_record = self.env['property.history'].sudo().create(history_vals)
                    _logger.info(
                        f"History created - ID: {history_record.id}, Field: {field_label}, Reason: '{self.reason}'")

        # إنشاء رسالة في Chatter
        change_summary = '<br/>'.join([f"• {change}" for change in changes])
        message = f"""
            <div style="padding: 15px; border-left: 4px solid #0066cc; 
                        background-color: #f0f8ff; border-radius: 5px;">
                <h4 style="margin-top: 0; color: #0066cc;">
                    Property Updated via Wizard
                </h4>
                <p><strong>Reason:</strong> {self.reason}</p>
                <p><strong>Changes Made:</strong></p>
                {change_summary}
                <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                    Changed by: {self.env.user.name}<br/>
                    Date: {fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        """
        self.property_id.message_post(
            body=message,
            subject='Property Change via Wizard',
            message_type='notification'
        )

        _logger.info(f"WIZARD: Changes applied successfully. Total changes: {len(changes)}")

        # إغلاق الويزرد والعودة لصفحة العقار مع تحديث
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'property',
            'res_id': self.property_id.id,
            'view_mode': 'form',
            'target': 'current',
            'context': self.env.context,
        }