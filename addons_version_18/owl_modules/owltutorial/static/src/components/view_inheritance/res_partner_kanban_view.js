/** @odoo-module */

import { registry } from "@web/core/registry"
import { kanbanView } from "@web/views/kanban/kanban_view"
import { KanbanController } from "@web/views/kanban/kanban_controller"
import { useService } from "@web/core/utils/hooks"

const { onWillStart } = owl

class ResPartnerKanbanController extends KanbanController {
  setup() {
    super.setup()
    this.action = useService("action")
    this.orm = useService("orm")

    onWillStart(async () => {
      this.customerLocations = await this.orm.readGroup("res.partner", [], ['state_id'], ['state_id'])
    })
  }

  openSalesView() {
    this.action.doAction({
      type: "ir.actions.act_window",
      name: "Customer Sales",
      res_model: "sale.order",
      views: [[false, "list"], [false, "form"]]
    })
  }

  selectLocations(state) {
    const id = state ? state[0] : false
    const name = state ? state[1] : "Undefined"

    let searchItems = this.env.searchModel.getSearchItems((item) => item.type === 'filter' && item.description === name)

    // If filter already exists, toggle it
    if (searchItems.length > 0) {
      const filter = searchItems[0];
      this.env.searchModel.toggleSearchItem(filter.id);
    } else {
      // If no filter exists, create one (it comes active by default)
      this.env.searchModel.createNewFilters([{
        description: name,
        domain: [['state_id', '=', id]],
        type: 'filter',
      }]);
    }
  }
}

ResPartnerKanbanController.template = "owl.ResPartnerKanbanView"

export const resPartnerKanbanView = {
  ...kanbanView,
  Controller: ResPartnerKanbanController,
  buttonTemplate: "owl.ResPartnerKanbanView.Buttons",
}

registry.category("views").add("res_partner_kanban_view", resPartnerKanbanView)