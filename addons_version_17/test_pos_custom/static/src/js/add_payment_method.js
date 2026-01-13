odoo.define("test_pos_custom.add_payment_method", function (require) {
  "use strict";

  var screens = require("point_of_sale.screens");
  var models = require("point_of_sale.models");
  models.load_fields("res.partner", ["code"]);

  screens.PaymentScreenWidget.include({
    show: function () {
      this._super(); // استدعاء الدالة الأصلية

      var order = this.pos.get_order().get_client(); // الحصول على الطلب الحالي
      var default_method = this.pos.config.default_payment_method;

      if (default_method) {
        this.clickPaymentMethod(default_method[0]); // اختيار طريقة الدفع الافتراضية
      }

      if (order) {
        console.log("Client Information:", order);
        console.log("Client Information:", order.code);
      } else {
        console.log("No client set for the current order.");
      }
    },
  });
});
