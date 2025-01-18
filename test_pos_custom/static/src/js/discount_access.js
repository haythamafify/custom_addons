odoo.define('test_pos_custom.discount_access', function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const DiscountButton = require("pos_discount.DiscountButton");
    const session = require("web.session");

    // تعريف فئة جديدة تمتد من DiscountButton
    const PosDiscountButton = class extends DiscountButton {
        async onClick() {
            const user_input = await this.showPopup('NumberPopup', {
                isPassword: true,
                title: this.env._t("Enter Password"),
                body: this.env._t("Please enter the password to apply discounts:"),
            });

            if (user_input && user_input.payload === this.env.pos.config.discount_pass_code) {
                // تنفيذ منطق الخصم إذا كانت كلمة المرور صحيحة
                console.log("Password is correct. Applying discount...");
            } else {
                // عرض رسالة خطأ إذا كانت كلمة المرور غير صحيحة
                this.showPopup('ErrorPopup', {
                    title: this.env._t("Error"),
                    body: this.env._t("Invalid Password"),
                });
            }
        }

        // التحقق من صلاحيات المستخدم قبل تشغيل الزر
        async button_click() {
            const hasGroup = await session.user_has_group('test_pos_custom.pos_group_discount');
            if (hasGroup) {
                // استدعاء الوظيفة الأصلية إذا كان لدى المستخدم الصلاحية
                super.onClick();
            } else {
                // منع الإجراء وعرض رسالة إذا لم يكن لديه الصلاحية
                this.showPopup('ErrorPopup', {
                    title: "Access Denied",
                    body: "You do not have permission to apply discounts.",
                });
            }
        }
    };

    // تسجيل المكون الجديد
    Registries.Component.add(PosDiscountButton);

    return PosDiscountButton;
});
