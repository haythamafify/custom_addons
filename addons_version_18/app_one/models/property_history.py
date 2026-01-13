import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class PropertyHistory(models.Model):
    _name = "property.history"
    _description = "Property Modification History"
    _order = "change_date desc, id desc"
    _rec_name = "property_id"

    # Basic Info (Read-only)
    property_id = fields.Many2one(
        'property',
        string='Property',
        required=True,
        readonly=True,
        ondelete='cascade',
        index=True
    )
    property_ref = fields.Char(
        string='Property Reference',
        readonly=True,
        help="Reference of the property at the time of change"
    )

    # Change Info
    change_date = fields.Datetime(
        string='Change Date',
        default=fields.Datetime.now,
        required=True,
        readonly=True,
        index=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Changed By',
        default=lambda self: self.env.user,
        required=True,
        readonly=True
    )
    change_type = fields.Selection([
        ('create', 'Created'),
        ('write', 'Modified'),
        ('state_change', 'State Changed'),
        ('price_change', 'Price Changed'),
        ('owner_change', 'Owner Changed')
    ], string='Change Type', required=True, readonly=True, index=True)

    # Field Changes
    field_name = fields.Char(
        string='Field Name',
        readonly=True,
        help="Technical field name that was changed"
    )
    field_label = fields.Char(
        string='Field Label',
        readonly=True,
        help="User-friendly field label"
    )
    old_value = fields.Text(string='Old Value', readonly=True)
    new_value = fields.Text(string='New Value', readonly=True)

    # Additional Context
    note = fields.Text(string='Notes', readonly=True)

    # ✅ حقل السبب - READONLY بعد الحفظ
    reason = fields.Text(
        string='Reason for Change',
        readonly=True,
        help='Explanation for why this change was made'
    )

    # Display name computed
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('property_id', 'change_type', 'change_date')
    def _compute_display_name(self):
        """Generate friendly display name"""
        for rec in self:
            property_name = rec.property_id.name or 'N/A'
            change_type_label = dict(
                self._fields['change_type'].selection
            ).get(rec.change_type, '')
            date_str = rec.change_date.strftime('%Y-%m-%d %H:%M') if rec.change_date else ''
            rec.display_name = f"{property_name} - {change_type_label} ({date_str})"

    def action_open_property(self):
        """Open related property form"""
        self.ensure_one()
        return {
            'name': _('Property: %s', self.property_id.name),
            'type': 'ir.actions.act_window',
            'res_model': 'property',
            'view_mode': 'form',
            'res_id': self.property_id.id,
            'target': 'current',
        }





class Property(models.Model):
    _inherit = "property"

    history_ids = fields.One2many(
        'property.history',
        'property_id',
        string='History',
        readonly=True
    )
    history_count = fields.Integer(
        string='History Count',
        compute='_compute_history_count'
    )

    @api.depends('history_ids')
    def _compute_history_count(self):
        """Count history records"""
        for rec in self:
            rec.history_count = len(rec.history_ids)

    def action_view_history(self):
        """Smart button to view property history"""
        self.ensure_one()
        return {
            'name': _('Property History: %s', self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'property.history',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'create': False, 'delete': False, 'edit': False},
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Track property creation"""
        records = super(Property, self).create(vals_list)

        for record in records:
            try:
                # Create history record for creation
                self.env['property.history'].sudo().create({
                    'property_id': record.id,
                    'property_ref': record.ref,
                    'change_type': 'create',
                    'field_label': 'Property Created',
                    'new_value': record.name,
                    'note': _('Property created with reference: %s', record.ref),
                    'reason': False  # No reason for creation
                })
                _logger.info(f"History tracked for new property: {record.name}")
            except Exception as e:
                _logger.error(f"Error tracking property creation: {str(e)}")

        return records

    def write(self, vals):
        """Track property modifications"""
        # ✅ تخطي History إذا تم الاستدعاء من الويزرد (لأنه ينشئ History بنفسه)
        if self.env.context.get('skip_history'):
            return super(Property, self).write(vals)

        # ✅ استخراج السبب من context إذا كان موجوداً (من الويزرد)
        reason_from_context = self.env.context.get('change_reason', False)

        # Debug logging
        if reason_from_context:
            _logger.info(f"✅ REASON FOUND IN CONTEXT: {reason_from_context}")
        else:
            _logger.warning(f"⚠️ NO REASON IN CONTEXT - Context keys: {list(self.env.context.keys())}")

        # Fields to track with their labels
        tracked_fields = {
            'name': _('Name'),
            'state': _('State'),
            'expected_price': _('Expected Price'),
            'selling_price': _('Selling Price'),
            'owner_id': _('Owner'),
            'date_availability': _('Available From'),
            'expected_date_selling': _('Expected Selling Date'),
            'bedrooms': _('Bedrooms'),
            'living_area': _('Living Area'),
            'user_id': _('Responsible'),
            'active': _('Active Status'),
            'facades': _('Facades'),
            'garage': _('Garage'),
            'garden': _('Garden'),
            'garden_area': _('Garden Area')
        }

        for record in self:
            try:
                for field_name, field_label in tracked_fields.items():
                    if field_name in vals:
                        old_value = self._format_field_value(record, field_name)
                        new_value = self._format_field_value_from_vals(vals, field_name)

                        # Only log if value actually changed
                        if old_value != new_value:
                            # Determine change type
                            change_type = 'write'
                            if field_name == 'state':
                                change_type = 'state_change'
                            elif field_name in ['expected_price', 'selling_price']:
                                change_type = 'price_change'
                            elif field_name == 'owner_id':
                                change_type = 'owner_change'

                            # ✅ Create history record WITH REASON
                            history_vals = {
                                'property_id': record.id,
                                'property_ref': record.ref,
                                'change_type': change_type,
                                'field_name': field_name,
                                'field_label': field_label,
                                'old_value': old_value,
                                'new_value': new_value,
                                'note': _('Field "%s" changed from "%s" to "%s"',
                                          field_label, old_value, new_value),
                                'reason': reason_from_context  # ✅ حفظ السبب
                            }

                            _logger.info(f"📝 Creating history with reason: {reason_from_context}")
                            _logger.info(f"📝 History vals: {history_vals}")

                            history_record = self.env['property.history'].sudo().create(history_vals)

                            _logger.info(
                                f"✅ History created with ID: {history_record.id}, Reason: {history_record.reason}")

                            _logger.info(
                                f"History tracked for {record.name}: "
                                f"{field_label} changed from '{old_value}' to '{new_value}'"
                                f"{' - Reason: ' + reason_from_context if reason_from_context else ''}"
                            )
            except Exception as e:
                _logger.error(f"Error tracking property modification: {str(e)}")

        return super(Property, self).write(vals)

    def _format_field_value(self, record, field_name):
        """Format field value for display in history"""
        value = record[field_name]

        if not value and value != 0:
            return _('Empty')

        # Handle Many2one fields
        if isinstance(value, models.BaseModel):
            return value.name_get()[0][1] if value else _('Empty')

        # Handle Selection fields
        if field_name in ['state', 'garden_orientation']:
            field_obj = record._fields[field_name]
            if hasattr(field_obj, 'selection'):
                selection_dict = dict(field_obj.selection)
                return selection_dict.get(value, str(value))

        # Handle Boolean
        if isinstance(value, bool):
            return _('Yes') if value else _('No')

        # Handle dates
        if isinstance(value, (fields.Date, fields.Datetime)):
            return str(value)

        return str(value)

    def _format_field_value_from_vals(self, vals, field_name):
        """Format field value from vals dictionary"""
        value = vals.get(field_name)

        if value is None or (value is False and not isinstance(value, bool)):
            return _('Empty')

        # Handle Many2one (stored as ID)
        if field_name in ['owner_id', 'user_id']:
            if value:
                model_name = 'owner' if field_name == 'owner_id' else 'res.users'
                record = self.env[model_name].browse(value)
                return record.name_get()[0][1] if record.exists() else str(value)
            return _('Empty')

        # Handle Selection
        if field_name in ['state', 'garden_orientation']:
            field_obj = self._fields[field_name]
            if hasattr(field_obj, 'selection'):
                selection_dict = dict(field_obj.selection)
                return selection_dict.get(value, str(value))

        # Handle Boolean
        if isinstance(value, bool):
            return _('Yes') if value else _('No')

        return str(value)
