# افتح ملفًا جديدًا للكتابة
with open("property_records.xml", "w", encoding="utf-8") as file:
    # اكتب بداية ملف XML
    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<odoo>\n')

    # إنشاء 50 سجلًا
    for i in range(1, 51):
        record = f'''
        <record id="property_{i:02d}" model="property">
            <field name="ref">new</field>
            <field name="name">Property {i:02d}</field>
            <field name="description">A beautiful property with many features.</field>
            <field name="postcode">{12344 + i}</field>
            <field name="date_availability">2025-01-13</field>
            <field name="expected_date_selling">2025-06-01</field>
            <field name="is_late">False</field>
            <field name="expected_price">{250000 + i * 10000}</field>
            <field name="diff">0.0</field>
            <field name="selling_price">0.0</field>
            <field name="bedrooms">{3 + i % 3}</field>
            <field name="living_area">{120 + i * 5}</field>
            <field name="facades">{2 + i % 2}</field>
            <field name="garage">True</field>
            <field name="garden">True</field>
            <field name="garden_area">{50 + i * 2}</field>
            <field name="garden_orientation">north</field>
            <field name="state">pending</field>
            <field name="create_time">2025-01-13 10:00:00</field>
            <field name="next_time">2025-01-15 10:00:00</field>
            <field name="active">True</field>
        </record>
        '''
        file.write(record)  # اكتب السجل في الملف

    # اكتب نهاية ملف XML
    file.write('</odoo>\n')