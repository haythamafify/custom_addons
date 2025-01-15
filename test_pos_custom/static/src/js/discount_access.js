odoo.define('test_pos_custom.discount_access', function (require) {
    "use strict";

    var DiscountButton = require("pos_discount.DiscountButton");
    var session = require("web.session");

    DiscountButton.include({
        button_click: function () {
        console.log("DiscountButton.button_click");
            var self = this; // لحفظ مرجع الكائن
            session.user_has_group('test_pos_custom.pos_group_discount').then(function (has_group) {
                if (has_group) {
                    // استدعاء الوظيفة الأصلية إذا كان المستخدم لديه الصلاحية
                   return self._super();
                } else {
                    // إذا لم يكن لدى المستخدم الصلاحية، عرض رسالة أو منع الإجراء
                    self.showPopup('ErrorPopup', {
                        title: "Access Denied",
                        body: "You do not have permission to apply discounts.",
                    });
                }
            });
        },
    });
});
