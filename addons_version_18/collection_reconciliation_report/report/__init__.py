# Import XLSX report only when report_xlsx (OCA) is available.
# This allows installation without the OCA dependency.
try:
    from odoo.addons.report_xlsx.models import report_xlsx  # noqa — confirms presence
    from . import collection_report_xlsx
except ImportError:
    pass
