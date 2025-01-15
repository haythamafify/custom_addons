odoo.define('test_pos_custom.add_payment_method', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    screens.PaymentScreenWidget.include({
show : function(){
        this._super();
     var default_method = this.pos.config.default_payment_method;
     if(default_method){
      this.clickPaymentMethod(default_method(0));
     }
     else{
     }
     }



});
