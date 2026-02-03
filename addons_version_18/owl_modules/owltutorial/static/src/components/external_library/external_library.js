/** @odoo-module **/
import { Component, onWillStart, onMounted, useRef, useState } from "@odoo/owl";
import { loadJS, loadCSS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

export class ExternalLibrary extends Component {
    static template = "owl_dashboard.ExternalLibrary";

    setup() {
        this._t = _t;
        this.phone = useRef("phone");
        this.iti = null;
        this.state = useState({ phoneValid: undefined });

        onWillStart(async () => {
            await loadJS(
                "https://cdn.jsdelivr.net/npm/intl-tel-input@26.0.6/build/js/intlTelInput.min.js"
            );
            await loadCSS(
                "https://cdn.jsdelivr.net/npm/intl-tel-input@26.0.6/build/css/intlTelInput.css"
            );
        });

        onMounted(() => {
            if (this.phone.el) {
                this.iti = window.intlTelInput(this.phone.el, {
                    initialCountry: "auto",
                    utilsScript:
                        "https://cdn.jsdelivr.net/npm/intl-tel-input@26.0.6/build/js/utils.js",
                });
            }
        });

        this.validate = this.validate.bind(this);
    }

    validate() {
        if (this.iti) {
            if (this.iti.isValidNumber()) {
                this.state.phoneValid = true;
                alert(_t("The phone number is valid: ") + this.iti.getNumber());
            } else {
                alert(_t("Invalid phone number!"));
                this.state.phoneValid = false;
            }
        }
    }
}

registry.category("actions").add("owl_dashboard.external_library", ExternalLibrary);
