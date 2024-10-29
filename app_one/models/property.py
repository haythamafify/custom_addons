
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class Property(models.Model):
    _name = "property"
    _description = "Property"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ref = fields.Char(default="new", raedonly="True")
    name = fields.Char(required=True)
    description = fields.Text(tracking=1)
    postcode = fields.Char(required=True)
    date_availability = fields.Date(default=fields.Date.today(), tracking=True)
    expected_date_selling = fields.Date(tracking=True)
    is_late = fields.Boolean()
    expected_price = fields.Float()
    diff = fields.Float(compute='_compute_diff', store=True, readonly=True)
    selling_price = fields.Float()
    bedrooms = fields.Integer(default=1)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean(groups="app_one.property_manager_group")
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West'), ('northeast', 'Northeast'),
         ('southeast', 'Southeast'), ('southwest', 'Southwest'), ('northwest', 'Northwest'),
         ('no_garden', 'No Garden')], string="Garden Orientation", default="north")
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), ('sold', 'Sold'), ('closed', 'Closed'), ],
                             default='pending')

    owner_id = fields.Many2one('owner', string="Owner")
    tag_ids = fields.Many2many("tags")
    owner_address = fields.Char(related="owner_id.address")
    owner_phone = fields.Char(related="owner_id.phone")
    line_ids = fields.One2many("property.line", "property_id")
    create_time = fields.Datetime(default=fields.Datetime.now)
    next_time = fields.Datetime(compute="_compute_next_time")
    _sql_constraints = [('unique_name', 'UNIQUE(name)', 'الاسم يجب ان لايتكرر.'),
                        ('price_positive', 'check(price > 0)', "السعر يجب ان يكون موجب ")]

    @api.depends('selling_price', 'expected_price')
    def _compute_diff(self):
        for rec in self:
            rec.diff = rec.selling_price - rec.expected_price

    @api.constrains('bedrooms')
    def _check_bedrooms_greater_zero(self):
        for rec in self:
            if rec.bedrooms == 0:
                raise ValidationError("The number of bedrooms must be greater than zero.")

    # Action methods for the buttons
    def action_draft(self):
        for rec in self:
            rec.create_history_record(rec.state, 'draft')
            rec.state = 'draft'

    def action_pending(self):
        for rec in self:
            rec.create_history_record(rec.state, 'pending')
            rec.state = 'pending'

    def action_sold(self):
        for rec in self:
            rec.create_history_record(rec.state, 'sold')
            rec.state = 'sold'

    def action_closed(self):
        for rec in self:
            rec.create_history_record(rec.state, 'closed')
            rec.state = 'closed'

    # automation action for check expected selling date
    def check_expect_selling_date(self):

        property_ids = self.search([])
        print(property_ids, "root")
        for rec in property_ids:
            print(rec, "rec")

            if rec.expected_date_selling and rec.expected_date_selling < fields.date.today():
                rec.is_late = True

    def action(self):

        # print(self.env['owner'].create({
        #     "name": "haytham gamal", "phone": "123456789"
        # }))
        print(self.env['property'].search(['!',('name','=','gggggggg'),('postcode','=','h')]))





    @api.model
    def create(self, vals):
        res = super(Property, self).create(vals)
        if res.ref == 'new':
            res.ref = self.env['ir.sequence'].next_by_code('property_seq')
        return res

    def create_history_record(self, old_state, new_state, reason=""):
        for rec in self:
            rec.env['property.history'].create(
                {'user_id': rec.env.uid,
                 'property_id': rec.id, 'old_state': old_state,
                 'new_state': new_state,
                 'reason': reason,
                 'line_ids': [(0, 0, {'description': line.description, 'area': line.area}) for line in rec.line_ids]
                 })

    def action_change_state_wizard(self):
        action = self.env['ir.actions.actions']._for_xml_id('app_one.change_state_wizard_action')
        action['context'] = {'default_property_id': self.id}
        return action

    @api.depends('create_time')
    def _compute_next_time(self):
        for rec in self:
            if rec.create_time:
                rec.next_time = rec.create_time + timedelta(hours=6)
            else:
                rec.next_time = False


class PropertyLine(models.Model):
    _name = "property.line"

    property_id = fields.Many2one("property")
    area = fields.Char()
    description = fields.Text()
