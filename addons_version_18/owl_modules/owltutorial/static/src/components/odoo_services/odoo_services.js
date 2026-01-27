/** @odoo-module **/
import { Component, useSubEnv, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";

export class OdooServicesComponent extends Component {
  static template = "owl.OdooServicesTemplate";
  static components = { Layout };
  
  setup() {
    console.log("Start Owl Services");
    
    this.display = {
      controlPanel: { "top-right": false, "bottom-right": false },
    };
    
    useSubEnv({
      config: this.env.config,
    });
    
    // Initialize Services
    this.notification = useService("notification");
    this.dialog = useService("dialog");
    this.effect = useService("effect");
    
    // Load theme from localStorage only
    const savedTheme = browser.localStorage.getItem("dark_theme") || "false";
    
    this.state = useState({
      dark_theme: savedTheme
    });
    
    console.log("Current theme:", this.state.dark_theme);
  }
  
  // ==================================================
  // Notification Service
  // ==================================================
  showNotification() {
    console.log("Show Notification");
    this.notification.add("Hello from Odoo!", {
      type: "success",
      sticky: true,
      buttons: [
        {
          name: "Notification Action",
          primary: true,
          onClick: () => {
            console.log("Notification Action clicked");
          },
        },
        {
          name: "Show me Again",
          primary: false,
          onClick: () => {
            this.showNotification();
          },
        },
      ],
    });
  }
  
  // ==================================================
  // Dialog Service
  // ==================================================
  showDialog() {
    console.log("Show Dialog");
    let actionTaken = false;
    this.dialog.add(ConfirmationDialog, {
      title: _t("Dialog Service"),
      body: _t("This is a sample dialog message!"),
      confirm: () => {
        actionTaken = true;
        console.log("Dialog confirmed");
      },
      cancel: () => {
        actionTaken = true;
        console.log("Dialog cancelled");
      },
      close: () => {
        if (!actionTaken) {
          console.log("Dialog closed without action");
        }
      },
    });
  }
  
  // ==================================================
  // Effect Service
  // ==================================================
  showEffect() {
    console.log("Show Effect");
    this.effect.add({
      type: "rainbow_man",
      message: _t("Congratulations! Effect is working!"),
      fadeout: "slow",
    });
  }
  
  // ==================================================
  // Toggle Theme - LocalStorage Only
  // ==================================================
  toggleTheme() {
    console.log("Toggle Theme");
    
    const newTheme = this.state.dark_theme === "false" ? "true" : "false";
    browser.localStorage.setItem("dark_theme", newTheme);
    this.state.dark_theme = newTheme;
    
    const message = newTheme === "true" 
      ? "Dark theme enabled!" 
      : "Light theme enabled!";
    
    this.notification.add(message, { 
      type: "success",
      sticky: false 
    });
    
    console.log("New theme:", this.state.dark_theme);
  }
}

registry.category("actions").add("owl.odoo_services", OdooServicesComponent);