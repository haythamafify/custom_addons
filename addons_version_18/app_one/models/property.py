import logging
from datetime import timedelta

import requests
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class Property(models.Model):
    _name = "property"
    _description = "Property Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _log_access = True

    # Basic Fields
    ref = fields.Char(default="new", readonly=True)
    name = fields.Char(required=True, tracking=True)
    description = fields.Text(tracking=True, translate=True, groups="app_one.property_manager_group"
                              )
    postcode = fields.Char(required=True)
    active = fields.Boolean(default=True)

    # Dates
    date_availability = fields.Date(
        string='Available From',
        default=fields.Date.today,
        tracking=True
    )
    expected_date_selling = fields.Date(tracking=True)
    is_late = fields.Boolean(default=False, copy=False)
    create_time = fields.Datetime(default=fields.Datetime.now)
    next_time = fields.Datetime()

    # Pricing
    expected_price = fields.Float(tracking=True)
    selling_price = fields.Float(tracking=True)
    diff = fields.Float(
        string='Price Difference',
        compute="_compute_diff",
        store=True
    )

    # Property Details
    bedrooms = fields.Integer(default=1)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('northeast', 'Northeast'),
        ('southeast', 'Southeast'),
        ('southwest', 'Southwest'),
        ('northwest', 'Northwest'),
        ('no_garden', 'No Garden')
    ], string="Garden Orientation", default="north")

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('closed', 'Closed')
    ], default='draft', tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True)

    # Relations
    owner_id = fields.Many2one("owner", tracking=True)
    owner_address = fields.Char(related="owner_id.address", store=True, readonly=False)
    owner_phone = fields.Char(related="owner_id.phone", store=True, readonly=False)
    tag_ids = fields.Many2many("tag")
    line_ids = fields.One2many("property.line", "property_id", string="Property Lines")

    # Responsible User
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True
    )

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'This property name already exists!')
    ]

    def generate_property_excel_report(self):
        """
        فتح تقرير Excel من خلال Controller
        Open Excel report via Controller
        """
        import json

        # جمع IDs العقارات المحددة
        property_ids = self.ids if self else []

        _logger.info(f"Generating Excel report for {len(property_ids)} properties")

        # الحصول على base URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # بناء URL
        url = f"{base_url}/property/xlsx_report"

        # إضافة property_ids كـ parameter
        if property_ids:
            url += f"?property_ids={json.dumps(property_ids)}"

        _logger.info(f"Redirecting to: {url}")

        # فتح URL في نافذة جديدة
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',  # فتح في تبويب جديد
        }

    # for test api only
    def get_properties_api(self):
        try:
            # محاولة إرسال الطلب
            res = requests.get(
                "http://localhost:8069/v1/property",
                auth=('admin', 'admin'),
                timeout=10  # انتظار 10 ثواني كحد أقصى
            )

            # التحقق من نجاح الطلب
            res.raise_for_status()  # يرفع exception لو الـ status code خطأ (404, 500, etc.)

            # طباعة النتيجة
            print("✓ نجح الطلب!")
            print(f"Status Code: {res.status_code}")
            print(f"Response: {res.content}")

            return res.json()  # إرجاع البيانات كـ Python dict

        except requests.exceptions.ConnectionError:
            # خطأ في الاتصال (السيرفر مش شغال مثلاً)
            print("✗ خطأ: لا يمكن الاتصال بالسيرفر")
            print("تأكد أن السيرفر شغال على localhost:8069")

        except requests.exceptions.Timeout:
            # انتهى وقت الانتظار
            print("✗ خطأ: انتهى وقت الانتظار")
            print("السيرفر بطيء جداً في الرد")

        except requests.exceptions.HTTPError as e:
            # خطأ في الـ HTTP (401, 404, 500, etc.)
            print(f"✗ خطأ HTTP: {e}")
            print(f"Status Code: {res.status_code}")
            print(f"Response: {res.content}")

        except requests.exceptions.RequestException as e:
            # أي خطأ آخر
            print(f"✗ حدث خطأ غير متوقع: {e}")

        except Exception as e:
            # خطأ عام (احتياطي)
            print(f"✗ خطأ برمجي: {e}")

        return None  # إرجاع None في حالة فشل الطلب

    @api.onchange("expected_price")
    def _change_in_expected_price(self):
        """Validate expected price on change"""
        if self.expected_price and self.expected_price <= 0:
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _("The value must be greater than zero"),
                    "type": "notification"
                }
            }

    @api.depends("selling_price", "expected_price")
    def _compute_diff(self):
        """Calculate price difference"""
        for rec in self:
            rec.diff = rec.selling_price - rec.expected_price

    @api.constrains("bedrooms")
    def _check_bedrooms_greater_than_zero(self):
        """Validate bedrooms count"""
        for rec in self:
            if rec.bedrooms <= 0:
                raise ValidationError(_("Bedrooms must be greater than zero."))

    def action_draft(self):
        """Set property to draft state"""
        self.write({'state': 'draft'})

    def action_pending(self):
        """Set property to pending state"""
        self.write({'state': 'pending'})

    def action_sold(self):
        """Set property to sold state"""
        self.write({'state': 'sold', 'is_late': False})

    def action_closed(self):
        """Set property to closed state"""
        self.write({'state': 'closed', 'is_late': False})

    def copy(self, default=None):
        """Override copy to add '(copy)' to name with sequential numbering"""
        # Handle multiple records
        if len(self) > 1:
            return self.env['property'].concat(*[rec.copy(default) for rec in self])

        # Handle single record
        default = dict(default or {})

        # Generate unique name if not provided
        if 'name' not in default:
            base_name = self.name
            copy_number = 1
            new_name = _("%s (copy)", base_name)

            # Find next available copy number
            while self.env['property'].search_count([('name', '=', new_name)]) > 0:
                copy_number += 1
                new_name = _("%s (copy %s)", base_name, copy_number)

            default['name'] = new_name

        return super(Property, self).copy(default)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ref', 'new') == 'new':
                vals['ref'] = self.env['ir.sequence'].next_by_code('property.property') or 'new'
        return super(Property, self).create(vals_list)

    @api.model
    def check_expected_date_selling(self):
        """
        Scheduled Action: Check properties for late and upcoming sales
        Runs daily with protection against duplicate execution

        Returns:
            dict: Execution summary with counts and status
        """
        try:
            today = fields.Date.context_today(self)

            # Prevent duplicate execution on same day
            last_check_key = 'property.last_check_date'
            last_check = self.env['ir.config_parameter'].sudo().get_param(last_check_key)

            if last_check == str(today):
                _logger.info(f"Property check already executed today ({today})")
                return {
                    'skipped': True,
                    'reason': 'Already checked today',
                    'date': today.isoformat()
                }

            # Get warning period from settings
            warning_days = int(
                self.env['ir.config_parameter'].sudo().get_param(
                    'property.warning_days',
                    default='7'
                )
            )
            warning_date = today + timedelta(days=warning_days)

            _logger.info(f"Starting property check - Date: {today}, Warning period: {warning_days} days")

            # ==================== LATE PROPERTIES ====================
            late_properties = self.search([
                ('expected_date_selling', '<', today),
                ('is_late', '=', False),
                ('state', 'not in', ['sold', 'closed'])
            ])

            for prop in late_properties:
                days_late = (today - prop.expected_date_selling).days

                # Mark as late
                prop.write({'is_late': True})

                # Post message in chatter
                prop.message_post(
                    body=self._get_late_message_html(days_late, prop.expected_date_selling),
                    subject=_("Late Property Alert"),
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment'
                )

                # Create activity for responsible user
                if prop.user_id:
                    prop.activity_schedule(
                        'mail.mail_activity_data_todo',
                        summary=_("Follow up late property: %s", prop.name),
                        note=_(
                            "Property is %s day(s) overdue.\n"
                            "Expected date: %s\n"
                            "Please contact customer immediately."
                        ) % (days_late, prop.expected_date_selling),
                        user_id=prop.user_id.id,
                        date_deadline=today + timedelta(days=1)
                    )

                _logger.warning(
                    f"Late property detected: {prop.name} (Ref: {prop.ref}) - {days_late} days late"
                )

            # ==================== UPCOMING SALES ====================
            soon_late_properties = self.search([
                ('expected_date_selling', '>=', today),
                ('expected_date_selling', '<=', warning_date),
                ('state', 'not in', ['sold', 'closed'])
            ])

            for prop in soon_late_properties:
                days_left = (prop.expected_date_selling - today).days

                # Create reminder activity only if very close (3 days or less)
                if days_left <= 3 and prop.user_id:
                    # Check if activity already exists to avoid duplicates
                    existing_activity = self.env['mail.activity'].search([
                        ('res_model', '=', 'property'),
                        ('res_id', '=', prop.id),
                        ('user_id', '=', prop.user_id.id),
                        ('summary', 'ilike', f'Upcoming sale: {prop.name}')
                    ], limit=1)

                    if not existing_activity:
                        prop.activity_schedule(
                            'mail.mail_activity_data_meeting',
                            summary=_("Upcoming sale: %s", prop.name),
                            note=_(
                                "Expected selling date is in %s day(s).\n"
                                "Date: %s\n"
                                "Please prepare and contact customer."
                            ) % (days_left, prop.expected_date_selling),
                            user_id=prop.user_id.id,
                            date_deadline=prop.expected_date_selling
                        )

                _logger.info(
                    f"Upcoming sale: {prop.name} (Ref: {prop.ref}) - {days_left} days remaining"
                )

            # Save last check date
            self.env['ir.config_parameter'].sudo().set_param(last_check_key, str(today))

            _logger.info(
                f"Property check completed - Late: {len(late_properties)}, "
                f"Upcoming: {len(soon_late_properties)}"
            )

            return {
                'success': True,
                'late_count': len(late_properties),
                'warning_count': len(soon_late_properties),
                'date_checked': today.isoformat(),
                'warning_days': warning_days
            }

        except Exception as e:
            _logger.error(f"Error in property check: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def action_open_change_wizard(self):
        """
        فتح معالج التغيير للعقار الحالي
        Open the change wizard for current property
        ✅ يمنع فتح الويزرد إذا كانت الحالة = closed
        """
        self.ensure_one()

        # ✅ التحقق من الحالة - منع فتح الويزرد إذا كانت closed
        if self.state == 'closed':
            raise UserError(_(
                'Cannot modify closed property!\n'
                'Property "%s" is in closed state and cannot be modified through the wizard.\n'
                'Please reopen the property first if you need to make changes.'
            ) % self.name)

        return {
            'name': _('Update Property with Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'property.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_property_id': self.id,
            }
        }

    def _get_late_message_html(self, days_late, expected_date):
        """Generate HTML message for late property alert"""
        return f"""
            <div style="padding: 15px; background-color: #fff3cd; 
                        border-left: 5px solid #ffc107; border-radius: 5px;">
                <h4 style="color: #856404; margin: 0 0 10px 0;">
                    ⚠️ {_('Late Property Alert')}
                </h4>
                <p style="margin: 5px 0;">
                    {_('This property is')} <strong>{days_late} {_('day(s) late')}</strong> 
                    {_('from the expected selling date')}.
                </p>
                <p style="margin: 5px 0; color: #856404;">
                    {_('Expected date')}: <strong>{expected_date}</strong>
                </p>
            </div>
        """

    owner_count = fields.Integer(
        string='Owner Count',
        compute='_compute_owner_count',
        store=False
    )

    @api.depends('owner_id')
    def _compute_owner_count(self):
        """Calculate number of owners (1 if exists, 0 otherwise)"""
        for record in self:
            record.owner_count = 1 if record.owner_id else 0

    def action_open_related_owner(self):
        """
        فتح صفحة المالك المرتبط بالعقار
        Open the owner form view for the property
        """
        self.ensure_one()

        _logger.info(f"Opening owner for property: {self.name} (Ref: {self.ref})")

        # التحقق من وجود مالك
        if not self.owner_id:
            raise UserError(_(
                'No Owner Assigned!\n'
                'Property "%s" does not have an owner assigned.\n'
                'Please assign an owner first.'
            ) % self.name)

        # فتح نموذج المالك
        return {
            'type': 'ir.actions.act_window',
            'name': _('Owner: %s', self.owner_id.name),
            'res_model': 'owner',
            'view_mode': 'form',
            'res_id': self.owner_id.id,
            'target': 'current',
            'context': dict(self.env.context),
        }


class PropertyLine(models.Model):
    _name = "property.line"
    _description = "Property Line Details"

    area = fields.Float()
    description = fields.Char()
    property_id = fields.Many2one(
        "property",
        string='Property',
        ondelete='cascade',
        required=True
    )
