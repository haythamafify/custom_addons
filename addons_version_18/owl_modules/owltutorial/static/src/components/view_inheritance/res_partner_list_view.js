/** @odoo-module */

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";

class ResPartnerListController extends ListController {
  static template = "owl.ResPartnerListView";

  setup() {
    super.setup();
    this.action = useService("action");
  }

  get actionMenuItems() {
    return {
      action: [
        {
          description: "View Sales Orders",
          callback: this.openSalesView.bind(this),
        },
        {
          description: "View Invoices",
          callback: this.openInvoicesView.bind(this),
        },
        {
          description: "View Meetings",
          callback: this.openMeetingsView.bind(this),
        },
      ],
    };
  }

  openSalesView() {
    this.action.doAction({
      type: "ir.actions.act_window",
      name: "Customer Sales",
      res_model: "sale.order",
      views: [
        [false, "list"],
        [false, "form"],
      ],
    });
  }

  openInvoicesView() {
    this.action.doAction({
      type: "ir.actions.act_window",
      name: "Customer Invoices",
      res_model: "account.move",
      domain: [["move_type", "=", "out_invoice"]],
      views: [
        [false, "list"],
        [false, "form"],
      ],
    });
  }

  openMeetingsView() {
    this.action.doAction({
      type: "ir.actions.act_window",
      name: "Meetings",
      res_model: "calendar.event",
      views: [
        [false, "list"],
        [false, "form"],
      ],
    });
  }


}

export const resPartnerListView = {
  ...listView,
  Controller: ResPartnerListController,
};

registry.category("views").add("res_partner_list_view", resPartnerListView);
