import logging

_logger = logging.getLogger(__name__)

from . import models
from . import report


def post_init_hook(env):
    """Register XLSX export action only when OCA report_xlsx is available."""
    if "report.report_xlsx.abstract" not in env.registry:
        _logger.info(
            "collection_reconciliation_report: OCA report_xlsx not installed — "
            "XLSX export disabled. Install reporting-engine from OCA to enable it."
        )
        return

    _logger.info("collection_reconciliation_report: Activating XLSX export.")
    env["base.automation"]  # warm registry
    import odoo.tools.convert as convert
    import os
    xml_file = os.path.join(os.path.dirname(__file__), "report", "collection_report_templates.xml")
    convert.convert_file(env, "collection_reconciliation_report", xml_file, {}, mode="init", noupdate=True)
