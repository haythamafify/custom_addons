/** @odoo-module **/

import { Component, onWillStart, onMounted, useRef } from "@odoo/owl";
import { loadJS, loadCSS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

export class FilePondLibrary extends Component {
  static template = "owl_dashboard.FilePondLibrary";

  setup() {
    this._t = _t;
    this.fileInput = useRef("fileInput");

    onWillStart(async () => {
      // FilePond core
      await loadJS("https://unpkg.com/filepond@4.32.11/dist/filepond.js");
      await loadCSS("https://unpkg.com/filepond@4.32.11/dist/filepond.css");

      // Image preview plugin
      await loadJS(
        "https://unpkg.com/filepond-plugin-image-preview@4.6.12/dist/filepond-plugin-image-preview.js"
      );
      await loadCSS(
        "https://unpkg.com/filepond-plugin-image-preview@4.6.12/dist/filepond-plugin-image-preview.css"
      );
    });

    onMounted(() => {
      // Register plugin FIRST
      FilePond.registerPlugin(FilePondPluginImagePreview);

      // Create instance
      FilePond.create(this.fileInput.el, {
        allowMultiple: true,
        server: {
          process: "/owl/filepond/process",
          revert: "/owl/filepond/revert",
        },
      });
    });
  }
}

registry
  .category("actions")
  .add("owl_dashboard.filepond_library", FilePondLibrary);
