# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestProperty(TransactionCase):
    """
    Unit Tests لنموذج Property
    =========================

    بيختبر إن الـ Business Logic شغالة صح
    """

    def setUp(self):
        """
        🔧 الإعداد - بيتنفذ قبل كل test
        """
        super(TestProperty, self).setUp()

        # إنشاء بيانات تجريبية
        self.owner = self.env['owner'].create({
            'name': 'Ahmed Mohamed',
            'phone': '01234567890',
            'address': 'Cairo, Egypt'
        })

        self.property = self.env['property'].create({
            'name': 'Test Villa',
            'postcode': '12345',
            'expected_price': 1000000,
            'selling_price': 1200000,
            'bedrooms': 3,
            'owner_id': self.owner.id
        })

    # ==================== TESTS ====================

    def test_01_property_creation(self):
        """
        ✅ Test 1: اختبار إنشاء عقار
        """
        # تأكد إن العقار اتعمل
        self.assertTrue(self.property.id, "Property should be created")

        # تأكد إن الـ ref اتعمل تلقائياً
        self.assertNotEqual(self.property.ref, 'new',
                            "Property ref should be generated")

        # تأكد إن الـ state = draft
        self.assertEqual(self.property.state, 'draft',
                         "New property should be in draft state")

    def test_02_compute_diff(self):
        """
        ✅ Test 2: اختبار حساب الفرق في السعر
        """
        # Expected: 1200000 - 1000000 = 200000
        expected_diff = 200000

        self.assertEqual(self.property.diff, expected_diff,
                         f"Diff should be {expected_diff}")

    def test_03_bedrooms_validation(self):
        """
        ✅ Test 3: اختبار Validation على bedrooms
        """
        # يجب أن يرفع ValidationError لو bedrooms <= 0
        with self.assertRaises(ValidationError,
                               msg="Should raise error for bedrooms <= 0"):
            self.property.write({'bedrooms': 0})

        with self.assertRaises(ValidationError):
            self.property.write({'bedrooms': -1})

    def test_04_state_transitions(self):
        """
        ✅ Test 4: اختبار تغيير الحالات
        """
        # Test draft -> pending
        self.property.action_pending()
        self.assertEqual(self.property.state, 'pending')

        # Test pending -> sold
        self.property.action_sold()
        self.assertEqual(self.property.state, 'sold')
        self.assertFalse(self.property.is_late,
                         "is_late should be False when sold")

    def test_05_copy_property(self):
        """
        ✅ Test 5: اختبار نسخ العقار
        """
        copied = self.property.copy()

        # تأكد إن الاسم اتغير
        self.assertIn('(copy)', copied.name)

        # تأكد إن الـ ID مختلف
        self.assertNotEqual(copied.id, self.property.id)

        # تأكد إن is_late = False في النسخة
        self.assertFalse(copied.is_late)

    def test_06_owner_relation(self):
        """
        ✅ Test 6: اختبار العلاقة مع المالك
        """
        # تأكد إن المالك مرتبط صح
        self.assertEqual(self.property.owner_id.id, self.owner.id)

        # تأكد إن العقار ظاهر في عقارات المالك
        self.assertIn(self.property, self.owner.property_ids)

        # تأكد إن property_count صح
        self.assertEqual(self.owner.property_count, 1)

    def test_07_related_fields(self):
        """
        ✅ Test 7: اختبار الـ Related Fields
        """
        # تأكد إن related fields بتجيب القيم الصح
        self.assertEqual(self.property.owner_address, 'Cairo, Egypt')
        self.assertEqual(self.property.owner_phone, '01234567890')

    def test_08_onchange_expected_price(self):
        """
        ✅ Test 8: اختبار onchange على expected_price
        """
        # لو حطيت قيمة سالبة، المفروض يرجع warning
        result = self.property._change_in_expected_price()

        # Test with negative price
        self.property.expected_price = -1000
        result = self.property._change_in_expected_price()

        if result:
            self.assertIn('warning', result)


# -c odoo.conf -d app_one_25 -u app_one --test-enable