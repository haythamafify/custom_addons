from odoo import models, fields, api
from odoo.exceptions import ValidationError


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
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([('north', 'North'),
                                           ('south', 'South'),
                                           ('east', 'East'),
                                           ('west', 'West'),
                                           ('northeast', 'Northeast'),
                                           ('southeast', 'Southeast'),
                                           ('southwest', 'Southwest'),
                                           ('northwest', 'Northwest'),
                                           ('no_garden', 'No Garden')], string="Garden Orientation", default="north")
    state = fields.Selection([('draft', 'Draft'),
                              ('pending', 'Pending'),
                              ('sold', 'Sold'),
                              ('closed', 'Closed'),
                              ], default='pending')

    owner_id = fields.Many2one('owner', string="Owner")
    tag_ids = fields.Many2many("tags")
    owner_address = fields.Char(related="owner_id.address")
    owner_phone = fields.Char(related="owner_id.phone")
    line_ids = fields.One2many("property.line", "property_id")

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'الاسم يجب ان لايتكرر.'),
        ('price_positive', 'check(price > 0)', "السعر يجب ان يكون موجب ")
    ]

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
            rec.state = 'draft'

    def action_pending(self):
        for rec in self:
            rec.state = 'pending'

    def action_sold(self):
        for rec in self:
            rec.state = 'sold'

    def action_closed(self):
        for rec in self:
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
        print(self.env['owner'].search([]))


class PropertyLine(models.Model):
    _name = "property.line"

    property_id = fields.Many2one("property")
    area = fields.Char()
    description = fields.Text()
