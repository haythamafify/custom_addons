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
    this.http = useService("http");
    this.orm = useService("orm");

    const stored = browser.localStorage.getItem(THEME_KEY);
    const initialDark = stored ? stored === "true" : false;

    this.state = useState({
      isDark: initialDark,
      get_http_data: null,
      post_http_data: null,
      rpc_data: null,
      orm_data: null,
      user_data: null,
      router_data: null,
      company_data: null,
      isLoading: false,
    });
  }

  // ---------- Computed Properties ----------
  get themeLabel() {
    return this.state.isDark ? _t("Dark Mode") : _t("Light Mode");
  }

  get themeIcon() {
    return this.state.isDark ? "Dark" : "Light";
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
    this.notification.add(_t("Hello from Odoo Services"), {
      type: "success",
      sticky: true,
      buttons: [
        {
          name: _t("Awesome"),
          primary: true,
          onClick: () => {
            console.log("[OdooServices] User clicked Awesome");
            this.showEffect();
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
        this.notification.add(_t("Action confirmed successfully"), {
          type: "success",
        });
      },
      cancel: () => {
        actionTaken = true;
        console.log("[OdooServices] User cancelled");
        this.notification.add(_t("Action cancelled"), {
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
      message: _t("Congratulations! You are awesome!"),
      fadeout: "slow",
    });
  }

  toggleTheme() {
    const newDark = !this.state.isDark;
    this.state.isDark = newDark;
    browser.localStorage.setItem(THEME_KEY, newDark ? "true" : "false");

    const message = newDark
      ? _t("Dark theme enabled")
      : _t("Light theme enabled");

    this.notification.add(message, {
      type: "success",
      sticky: false,
    });
  }

  async gethttpService() {
    const http = this.env.services.http;
    this.state.isLoading = true;

    try {
      const data = await http.get("https://dummyjson.com/products");
      console.log("[HTTP GET] Data received:", data);

      this.state.get_http_data = data;

      this.notification.add(_t("Data fetched successfully"), {
        type: "success",
      });
    } catch (error) {
      console.error("[HTTP GET Error]", error);
      this.notification.add(_t("Failed to fetch data"), {
        type: "danger",
      });
    } finally {
      this.state.isLoading = false;
    }
  }

  async posthttpService() {
    const http = this.env.services.http;
    this.state.isLoading = true;

    try {
      const newProduct = {
        title: "BMW Pencil",
        price: 15.99,
      };

      const data = await http.post("https://dummyjson.com/products/add", {
        body: JSON.stringify(newProduct),
        headers: {
          "Content-Type": "application/json",
        },
      });

      console.log("[HTTP POST] Response:", data);

      this.state.post_http_data = data;

      this.notification.add(_t("Data sent successfully"), {
        type: "success",
      });
    } catch (error) {
      console.error("[HTTP POST Error]", error);
      this.notification.add(_t("Failed to send data"), {
        type: "danger",
      });
    } finally {
      this.state.isLoading = false;
    }
  }

  async getRpcService() {
    this.state.isLoading = true;

    try {
      const response = await fetch("/owl/rpc_service", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ limit: 15 }),
      });

      // Check if response is ok first
      if (!response.ok) {
        const text = await response.text();
        console.error("[RPC Service] HTTP Error:", response.status, text);
        throw new Error(`HTTP ${response.status}: ${text.substring(0, 100)}`);
      }

      const responseData = await response.json();
      console.log("[RPC Service] Response:", responseData);

      if (!responseData.success) {
        throw new Error(responseData.message || "Server returned error");
      }

      this.state.rpc_data = responseData.data;

      this.notification.add(_t("RPC data fetched successfully"), {
        type: "success",
      });
    } catch (error) {
      console.error("[RPC Service Error]", error);
      this.notification.add(_t("Failed to fetch RPC data: ") + error.message, {
        type: "danger",
      });
    } finally {
      this.state.isLoading = false;
    }
  }

  async getOrmService() {
    this.state.isLoading = true;

    try {
      this.state.orm_data = await this.orm.searchRead(
        "res.partner",
        [],
        ["id", "name", "email", "phone"],
      );

      this.notification.add(
        `Loaded ${this.state.orm_data.length} partners successfully`,
        { type: "success" },
      );
    } catch (error) {
      console.error("ORM Error:", error);
      this.notification.add("Failed to load partners", {
        type: "danger",
      });
    } finally {
      this.state.isLoading = false;
    }
  }

  executeActionService() {
    const action = this.env.services.action;
    action.doAction({
      type: "ir.actions.act_window",
      name: "Action Service",
      res_model: "res.partner",
      domain: [],
      context: {},
      views: [
        [false, "list"],
        [false, "form"],
        [false, "kanban"],
      ],
      view_mode: "list,form,kanban",
      target: "current",
    });
  }

  testRouterService() {
    try {
      // Get current URL and router info from browser
      const currentUrl = browser.location.href;
      const currentPath = browser.location.pathname;
      const currentSearch = browser.location.search;
      const currentHash = browser.location.hash;

      console.log("[Router Service] Current URL:", currentUrl);

      // Extract route information
      const routeInfo = {
        url: currentUrl,
        path: currentPath,
        search: currentSearch || "No search parameters",
        hash: currentHash || "No hash",
        protocol: browser.location.protocol,
        host: browser.location.host,
      };

      this.state.router_data = JSON.stringify(routeInfo, null, 2);

      this.notification.add(_t("Router information loaded"), {
        type: "success",
      });
    } catch (error) {
      console.error("[Router Service Error]", error);
      this.notification.add(_t("Router service error: ") + error.message, {
        type: "danger",
      });
    }
  }

  async testUserService() {
    this.state.isLoading = true;
    try {
      // Fetch current user data using ORM
      const users = await this.orm.searchRead(
        "res.users",
        [["id", "=", 2]], // Current user is usually ID 2 (admin)
        ["id", "name", "email", "login", "company_id"],
      );

      if (users && users.length > 0) {
        const user = users[0];
        const userData = {
          id: user.id,
          name: user.name,
          email: user.email,
          login: user.login,
          company: user.company_id ? user.company_id[1] : "N/A",
        };
        this.state.user_data = JSON.stringify(userData);

        this.notification.add(_t("User data loaded: ") + user.name, {
          type: "success",
        });
      } else {
        this.notification.add(_t("No user data found"), {
          type: "warning",
        });
      }
    } catch (error) {
      console.error("[User Service Error]", error);
      this.notification.add(_t("User service error: ") + error.message, {
        type: "danger",
      });
    } finally {
      this.state.isLoading = false;
    }
  }

  testCompanyService() {
    try {
      const company = this.env.services.company;
      console.log("[Company Service]", company);

      if (company) {
        // Extract company information
        const companyInfo = {
          allowedCompanies: company.allowedCompanies,
          currentCompany: company.currentCompany,
          activeCompanyIds: company.activeCompanyIds,
        };
        this.state.company_data = JSON.stringify(companyInfo, null, 2);

        this.notification.add(_t("Company information loaded"), {
          type: "success",
        });
      } else {
        this.notification.add(_t("Company service not available"), {
          type: "warning",
        });
      }
    } catch (error) {
      console.error("[Company Service Error]", error);
      this.notification.add(_t("Company service error: ") + error.message, {
        type: "danger",
      });
    }
  }
}

registry.category("actions").add("owl.odoo_services", OdooServicesComponent);
