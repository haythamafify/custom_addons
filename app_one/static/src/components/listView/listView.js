
/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class ListViewActions extends Component {
    static template = "app_one.ListView";
}

registry.category("actions").add("app_one.actions_list_view", ListViewActions);