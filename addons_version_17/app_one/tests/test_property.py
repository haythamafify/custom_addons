from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError

class TestProperty(TransactionCase):

    def setUp(self):
        super(TestProperty, self).setUp()
        # إعداد بيانات الاختبار، مثل إنشاء مالك
        self.owner = self.env['owner'].create({
            'name': 'Test Owner',
            'phone': '123456789',
            'address': '123 Test St.'
        })


    def test_create_property(self):
        """ اختبار إنشاء ملكية جديدة """
        property_vals = {
            'name': 'Test Property',
            'postcode': '12345',
            'owner_id': self.owner.id,
            'expected_price': 200000,
            'selling_price': 220000,
            'bedrooms': 3,
        }
        property_record = self.env['property'].create(property_vals)
        self.assertEqual(property_record.name, 'Test Property')  # تحقق من الاسم
        self.assertTrue(property_record.ref.startswith('prt'),
                        "المرجع يجب أن يبدأ بـ 'prt'")  # تحقق من أن القيمة ليست فارغة

    def test_bedrooms_constraint(self):
        """ اختبار قيود عدد غرف النوم """
        with self.assertRaises(ValidationError):
            self.env['property'].create({
                'name': 'Invalid Property',
                'postcode': '12345',
                'owner_id': self.owner.id,
                'bedrooms': 0,  # قيمة غير صحيحة
            })
