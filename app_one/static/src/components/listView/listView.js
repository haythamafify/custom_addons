/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ListViewActions extends Component {
    static template = "app_one.ListView"; // اسم القالب المستخدم

    setup() {
        // استخدام useState لجعل المتغير تفاعليًا
        this.state = useState({
             properties: [], // قائمة الوحدات التي تم إنشاؤها});
        });
        this.orm = useService("orm"); // استخدام الخدمة الأساسية للأنظمة الأساسية
        this.rpc = useService("rpc"); // استخدام الخدمة الأساسية للأنظمة الأساسية
       // this.LoadRecords(); // تحميل السجلات عند تهيئة المكون
        this.load_records_rpc(); // تحميل السجلات بواسطة الرابط الخاص بالخدمة الأساسية

    }

    async LoadRecords() {
        try {
            const result = await this.orm.searchRead(  "property", [],[]);

            this.state.properties = result; // تحديث المتغير التفاعلي
            console.log(result); // عرض النتيجة في وحدة التحكم
        } catch (error) {
            console.error("Failed to load records:", error); // معالجة الأخطاء
        }
    }



async load_records_rpc() {
    try {
        const res = await this.rpc("web/dataset/call_kw", {
            model: "property",
            method: "search_read",
            args: [[]], // يمكنك تحديد شروط البحث هنا إذا لزم الأمر
            kwargs: {
                fields: [
                    "ref",
                    "name",
                    "description",
                    "postcode",
                    "date_availability",
                    "expected_date_selling",
                    "state",
                    "owner_id",
                    "tag_ids"
                ],
            },
        });

        // معالجة البيانات المستلمة
        console.log("Loaded records:", res);
        this.state.properties = res; // إذا كنت تستخدم حالة لتخزين البيانات
    } catch (error) {
        console.error("Failed to load records:", error); // معالجة الأخطاء
    }
}




}

// تسجيل المكون كإجراء (action)
registry.category("actions").add("app_one.actions_list_view", ListViewActions);