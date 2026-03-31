# HR Contract No End Date Alert

![Odoo](https://img.shields.io/badge/Odoo-18.0-875A7B?style=flat-square&logo=odoo&logoColor=white)
![License](https://img.shields.io/badge/License-LGPL--3-blue?style=flat-square)
![Category](https://img.shields.io/badge/Category-Human%20Resources-green?style=flat-square)
![Version](https://img.shields.io/badge/Version-18.0.1.0.0-orange?style=flat-square)

> Protect your organization from accidentally saving employee contracts without an end date.

---

## 📋 Overview

**HR Contract No End Date Alert** is an Odoo 18 module that shows a confirmation dialog before saving a contract with no end date, logs the decision to the Chatter, and provides a quick search filter to find all open-ended contracts.

---

## ✨ Features

| Feature | Description |
|---|---|
| ⚠️ **Smart Save Alert** | Confirmation dialog appears when saving a contract without an end date |
| 💬 **Chatter Tracking** | `skip_end_date_check` field is tracked — every decision is logged automatically |
| 🔍 **Search Filter** | "Contracts Without End Date" filter added to the contract search bar |
| 🎨 **Visual Highlight** | End Date field is visually highlighted (bold + warning color) when empty |
| 🌍 **i18n Support** | Arabic & English translations included (`.po` files) |
| 📋 **Auto Chatter Message** | A notification is posted to the Chatter when a contract is saved open-ended |

---

## 🚀 Installation

1. Copy the `hr_contract_no_end_date_alert` folder into your Odoo addons directory.
2. Restart the Odoo server.
3. Go to **Apps → Update Apps List**.
4. Search for **"HR Contract No End Date Alert"** and click **Install**.

> ⚠️ Requires Odoo **18.0** with the `hr_contract` module installed.

---

## ⚙️ Configuration

No configuration required. The module works immediately after installation with default Odoo HR contracts.

---

## 🏗️ Module Structure

```
hr_contract_no_end_date_alert/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── hr_contract.py           # skip_end_date_check field + Chatter messages
├── views/
│   └── hr_contract_views.xml    # Form view decoration + search filter
├── static/
│   └── src/
│       └── js/
│           └── hr_contract_form.js  # FormController patch → save dialog
├── i18n/
│   └── ar_001.po                # Arabic translations
├── security/
│   └── ir.model.access.csv
└── static/description/
    ├── index.html               # App Store description page
    ├── banner.svg               # App Store banner (1200×300)
    └── icon.svg                 # App Store icon (256×256)
```

---

## 🔄 How It Works

1. **User opens or creates an HR contract** — the module is transparent, no extra visible fields.
2. **User tries to save without filling End Date** — a dialog appears:
   > _"⚠️ Contract End Date Missing — Do you want to continue saving?"_
3. **If confirmed** — the contract is saved, `skip_end_date_check` is set to `True`, and a Chatter notification is posted automatically.
4. **Managers can filter** — using the "Contracts Without End Date" search filter to audit all open-ended contracts.

---

## 📄 License

This module is licensed under [LGPL-3](https://www.gnu.org/licenses/lgpl-3.0.html).

---

## 👤 Author

**Haytham Afify** | haythamgamal6@gmail.com

🐙 **GitHub:** [github.com/haythamafify](https://github.com/haythamafify)
💼 **LinkedIn:** [linkedin.com/in/haytham-gamal-4165797a](https://www.linkedin.com/in/haytham-gamal-4165797a/)
