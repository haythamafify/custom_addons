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
            isDark: initialDark, // Boolean حقيقي
        });
    }

    // ---------- Helpers ----------
    get themeLabel() {
        return this.state.isDark ? _t("Dark Mode") : _t("Light Mode");
    }

    get toggleButtonLabel() {
        return this.state.isDark
            ? _t("Switch to Light Theme")
            : _t("Switch to Dark Theme");
    }

    // ---------- Notification ----------
    showNotification() {
        this.notification.add(_t("Hello from Odoo!"), {
            type: "success",
            sticky: true,
            buttons: [
                {
                    name: _t("Notification Action"),
                    primary: true,
                    onClick: () => {
                        console.log("[OdooServices] Notification Action clicked");
                    },
                },
                {
                    name: _t("Show me Again"),
                    primary: false,
                    onClick: () => this.showNotification(),
                },
            ],
        });
    }

    // ---------- Dialog ----------
    showDialog() {
        let actionTaken = false;

        this.dialog.add(ConfirmationDialog, {
            title: _t("Dialog Service"),
            body: _t("This is a sample dialog message!"),
            confirm: () => {
                actionTaken = true;
                console.log("[OdooServices] Dialog confirmed");
            },
            cancel: () => {
                actionTaken = true;
                console.log("[OdooServices] Dialog cancelled");
            },
            close: () => {
                if (!actionTaken) {
                    console.log("[OdooServices] Dialog closed without action");
                }
            },
        });
    }

    // ---------- Effect ----------
    showEffect() {
        this.effect.add({
            type: "rainbow_man",
            message: _t("Congratulations! Effect is working!"),
            fadeout: "slow",
        });
    }

    // ---------- Theme ----------
    toggleTheme() {
        const newDark = !this.state.isDark;
        this.state.isDark = newDark;
        browser.localStorage.setItem(THEME_KEY, newDark ? "true" : "false");

        const message = newDark
            ? _t("Dark theme enabled!")
            : _t("Light theme enabled!");

        this.notification.add(message, {
            type: "success",
            sticky: false,
        });
    }
}

registry.category("actions").add("owl.odoo_services", OdooServicesComponent);
