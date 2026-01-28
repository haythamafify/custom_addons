/** @odoo-module **/
import { Component, useSubEnv, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";

const THEME_KEY = "dark_theme";

export class OdooServicesComponent extends Component {
  static template = "owl.OdooServicesTemplate";
  static components = { Layout };

  setup() {
    this.display = {
      controlPanel: { "top-right": false, "bottom-right": false },
    };

    useSubEnv({ config: this.env.config });

    this.notification = useService("notification");
    this.dialog = useService("dialog");
    this.effect = useService("effect");

    const stored = browser.localStorage.getItem(THEME_KEY);
    const initialDark = stored ? stored === "true" : false;

    this.state = useState({
      isDark: initialDark,
      get_http_data: null,
      post_http_data: null,
    });
  }

  // ---------- Computed Properties ----------
  get themeLabel() {
    return this.state.isDark ? _t("Dark Mode") : _t("Light Mode");
  }

  get themeIcon() {
    return this.state.isDark ? "🌙" : "☀️";
  }

  get themeClass() {
    return this.state.isDark ? "bg-dark text-white" : "bg-light";
  }

  get toggleButtonLabel() {
    return this.state.isDark
      ? _t("Switch to Light Theme")
      : _t("Switch to Dark Theme");
  }

  // ---------- Services ----------
  showNotification() {
    this.notification.add(_t("Hello from Odoo! 🎉"), {
      type: "success",
      sticky: true,
      buttons: [
        {
          name: _t("Awesome!"),
          primary: true,
          onClick: () => {
            console.log("[OdooServices] User clicked Awesome!");
            this.showEffect(); // Bonus: تشغيل Effect تلقائياً
          },
        },
        {
          name: _t("Show Again"),
          primary: false,
          onClick: () => this.showNotification(),
        },
      ],
    });
  }

  showDialog() {
    let actionTaken = false;

    this.dialog.add(ConfirmationDialog, {
      title: _t("Confirmation Dialog"),
      body: _t(
        "Are you sure you want to continue? This action cannot be undone.",
      ),
      confirm: () => {
        actionTaken = true;
        console.log("[OdooServices] User confirmed");
        this.notification.add(_t("Action confirmed!"), {
          type: "success",
        });
      },
      cancel: () => {
        actionTaken = true;
        console.log("[OdooServices] User cancelled");
        this.notification.add(_t("Action cancelled."), {
          type: "info",
        });
      },
      close: () => {
        if (!actionTaken) {
          console.log("[OdooServices] Dialog closed without action");
        }
      },
    });
  }

  showEffect() {
    this.effect.add({
      type: "rainbow_man",
      message: _t("🎉 Congratulations! You're awesome! 🌟"),
      fadeout: "slow",
    });
  }

  toggleTheme() {
    const newDark = !this.state.isDark;
    this.state.isDark = newDark;
    browser.localStorage.setItem(THEME_KEY, newDark ? "true" : "false");

    const icon = newDark ? "🌙" : "☀️";
    const message = newDark
      ? _t(`${icon} Dark theme enabled!`)
      : _t(`${icon} Light theme enabled!`);

    this.notification.add(message, {
      type: "success",
      sticky: false,
    });
  }


async gethttpService() {
  const http = this.env.services.http;
  
  try {
    const data = await http.get('https://dummyjson.com/products');
    console.log(data);
    
    this.state.get_http_data = data;  
    
    this.notification.add(_t("تم جلب البيانات بنجاح"), {
      type: "success",
    });
  } catch (error) {
    console.error(error);
    this.notification.add(_t("فشل جلب البيانات"), {
      type: "danger",
    });
  }
}


async posthttpService() {
  const http = this.env.services.http;

  try {
    const newProduct = {
      title: 'BMW Pencil',
      price: 15.99
    };
    
    const data = await http.post('https://dummyjson.com/products/add', {
      body: JSON.stringify(newProduct),
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log(data);
    
    this.state.post_http_data = data;
    
    this.notification.add(_t("Data sent successfully"), {
      type: "success",
    });
  } catch (error) {
    console.error(error);
    this.notification.add(_t("Failed to send data"), {
      type: "danger",
    });
  }
}





}

registry.category("actions").add("owl.odoo_services", OdooServicesComponent);
