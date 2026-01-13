# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'
    _description = 'Invoice with Property Integration'

    # ==================== FIELDS ====================

    # ✅ ربط العقار بالفاتورة
    property_id = fields.Many2one(
        'property',
        string='Related Property',
        tracking=True,
        domain="[('state', '=', 'sold')]",
        help="Link this invoice to a sold property"
    )

    # ✅ معلومات العقار (للعرض فقط - Related Fields)
    property_ref = fields.Char(
        related='property_id.ref',
        string='Property Reference',
        readonly=True
    )

    property_postcode = fields.Char(
        related='property_id.postcode',
        string='Property Postcode',
        readonly=True
    )

    property_selling_price = fields.Float(
        related='property_id.selling_price',
        string='Property Price',
        readonly=True
    )

    # ✅ للـ Smart Button
    property_count = fields.Integer(
        compute='_compute_property_count',
        string='Property Count'
    )

    # ==================== COMPUTE METHODS ====================

    @api.depends('property_id')
    def _compute_property_count(self):
        """حساب عدد العقارات المرتبطة"""
        for record in self:
            record.property_count = 1 if record.property_id else 0

    # ==================== ACTION METHODS ====================

    def action_view_property(self):
        """فتح العقار من الفاتورة"""
        self.ensure_one()

        if not self.property_id:
            raise UserError(_(
                'No Property Linked!\n'
                'This invoice is not linked to any property.'
            ))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Property: %s', self.property_id.name),
            'res_model': 'property',
            'view_mode': 'form',
            'res_id': self.property_id.id,
            'target': 'current',
        }

    # ==================== ONCHANGE METHODS ====================

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """
        ✅ لما تختار عقار:
        - يملأ معلومات العميل تلقائياً
        - يضيف سطر فاتورة بسعر العقار
        """
        if self.property_id:
            # ملء معلومات العميل من partner_id المالك
            if self.property_id.owner_id:
                owner = self.property_id.owner_id
                # ✅ تحقق من وجود partner_id قبل الاستخدام
                if hasattr(owner, 'partner_id') and owner.partner_id:
                    self.partner_id = owner.partner_id
                else:
                    # ✅ إنشاء partner جديد من بيانات المالك إذا لم يكن موجود
                    if owner.name:
                        partner = self.env['res.partner'].search([
                            ('name', '=', owner.name)
                        ], limit=1)

                        if not partner:
                            # إنشاء partner جديد
                            partner = self.env['res.partner'].create({
                                'name': owner.name,
                                'phone': owner.phone or False,
                                'street': owner.address or False,
                            })
                            # ربطه بالمالك
                            owner.write({'partner_id': partner.id})

                        self.partner_id = partner

            # ✅ إضافة سطر فاتورة تلقائياً (فقط إذا الفاتورة فاضية)
            if not self.invoice_line_ids:
                self.invoice_line_ids = [(0, 0, {
                    'name': _('Property Sale: %s', self.property_id.name),
                    'quantity': 1,
                    'price_unit': self.property_id.selling_price or 0.0,
                })]

    # ==================== OVERRIDE METHODS ====================

    def action_post(self):
        """
        ✅ عند ترحيل الفاتورة:
        - سجل رسالة في chatter العقار
        """
        result = super(AccountMoveInherit, self).action_post()

        for move in self:
            if move.property_id and move.move_type == 'out_invoice':
                # تسجيل رسالة في العقار
                move.property_id.message_post(
                    body=_('Invoice %s has been posted for this property with amount %s %s.') % (
                        move.name,
                        move.amount_total,
                        move.currency_id.symbol
                    ),
                    subject=_('Invoice Posted'),
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment'
                )

        return result



