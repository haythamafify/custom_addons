# App One - Property Management Module

A comprehensive Odoo module for managing properties, buildings, owners, and related transactions.

## Features

- **Property Management**: Create and manage property records with detailed information
- **Building Management**: Organize properties by buildings
- **Owner Management**: Track property owners and their details
- **Sales Integration**: Manage sales orders for properties
- **Account Integration**: Handle account moves and financial records
- **Property History**: Maintain historical records of property changes
- **Reports**: Generate property reports in multiple formats (XLSX, XML)
- **Multi-language Support**: Arabic (ar_001) localization included

## Module Structure

```
controllers/     - API endpoints for property management
data/           - Initial data and sequences
i18n/           - Translation files
models/         - Core business logic and database models
report/         - Report definitions and generators
security/       - Access control and security rules
static/         - CSS, JavaScript, and frontend components
tests/          - Unit tests
views/          - XML view definitions
wizard/         - Wizard dialogs for user interactions
```

## Models

- **Property**: Main property records
- **Building**: Building information and structure
- **Owner**: Property owner details
- **Clients**: Client management
- **Sale Order**: Sales order integration
- **Account Move**: Financial transaction management
- **Property History**: Historical tracking
- **Tag**: Property categorization

## API Endpoints

- Property API v2 (`property_api_v2.py`)
- Property API v1 (`property_api.py`)

## Installation

1. Place this module in your Odoo addons directory
2. Update the module list
3. Install the module from Apps menu

## Requirements

- Odoo 18.0 or compatible version
- Depends on base Odoo modules as defined in `__manifest__.py`

## License

Refer to the `__manifest__.py` for license information.
