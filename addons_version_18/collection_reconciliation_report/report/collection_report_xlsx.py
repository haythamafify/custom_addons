import base64
import logging
from io import BytesIO

from odoo import _, fields, models

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# XLSX report — the class body is defined once.  The _inherit is set only
# when the OCA report_xlsx abstract model is present in the registry.
#
# Pattern: define the implementation in a plain Python base class, then
# create the Odoo model class dynamically so _inherit is only evaluated when
# the parent actually exists.  This avoids the KeyError / TypeError that
# Odoo raises at registry build time when _inherit points to a missing model.
# ---------------------------------------------------------------------------


def _build_xlsx_class():
    """Return the Odoo AbstractModel class if report_xlsx is available, else None."""
    try:
        # Confirms that report_xlsx is installed before we reference its model.
        from odoo.addons.report_xlsx.models import report_xlsx as _rr  # noqa: F401
    except ImportError:
        _logger.debug(
            "collection_reconciliation_report: report_xlsx not found — "
            "XLSX export class will not be registered."
        )
        return None

    class CollectionReconciliationReportXlsx(models.AbstractModel):
        _name = "report.collection_reconciliation_report.collection_reconciliation_report_xlsx"
        _description = "Collection Reconciliation XLSX"
        _inherit = "report.report_xlsx.abstract"

        def _log_export(self, records):
            logging_model = self.env["collection.reconciliation.report"]
            logging_model._log_structured(
                "info",
                "collection_report_export_xlsx",
                record_count=len(records),
                grouped_by=self.env.context.get("group_by") or "",
                company_id=self.env.company.id,
            )

        def _group_records(self, records):
            group_by = self.env.context.get("group_by") or []
            if isinstance(group_by, str):
                group_by = [group_by]
            groups = []
            current_key = None
            current_label = None
            bucket = self.env[records._name]
            ordered_records = records.sorted(
                key=lambda r: (
                    tuple(
                        (getattr(r, fn.split(":")[0]).display_name
                         if getattr(r, fn.split(":")[0], False) else "")
                        if hasattr(getattr(r, fn.split(":")[0], False), "display_name")
                        else str(getattr(r, fn.split(":")[0], "") or "")
                        for fn in group_by
                    ),
                    r.payment_date or fields.Date.today(),
                    r.payment_name or "",
                )
            )
            for record in ordered_records:
                values = []
                labels = []
                for field_name in group_by:
                    clean_name = field_name.split(":")[0]
                    value = getattr(record, clean_name)
                    if hasattr(value, "display_name"):
                        values.append(value.id or 0)
                        labels.append(value.display_name or _("Undefined"))
                    else:
                        values.append(value or False)
                        labels.append(str(value or _("Undefined")))
                key = tuple(values)
                if key != current_key:
                    if bucket:
                        groups.append((current_label, bucket))
                    current_key = key
                    current_label = " / ".join(labels) if labels else _("All Records")
                    bucket = self.env[records._name].browse()
                bucket |= record
            if bucket:
                groups.append((current_label, bucket))
            return groups

        def _write_header(self, sheet, workbook, formats):
            headers = [
                _("Payment Date"), _("Payment Ref"), _("Invoice"),
                _("Customer"), _("Salesperson"), _("Company"), _("Journal"),
                _("Currency"), _("Collected"), _("Invoice Total"),
                _("Residual"), _("Invoice Date"), _("Due Date"),
                _("Delay Days"), _("Products"), _("Memo"),
            ]
            for col, header in enumerate(headers):
                sheet.write(0, col, header, formats["header"])
            sheet.set_row(0, 20)

        def _write_record(self, sheet, row, record, formats):
            def fmt_date(d):
                return d.strftime("%Y-%m-%d") if d else ""

            sheet.write(row, 0, fmt_date(record.payment_date), formats["date"])
            sheet.write(row, 1, record.payment_name or "", formats["text"])
            sheet.write(row, 2, record.invoice_name or "", formats["text"])
            sheet.write(row, 3, record.partner_id.display_name if record.partner_id else "", formats["text"])
            sheet.write(row, 4, record.salesperson_id.name if record.salesperson_id else "", formats["text"])
            sheet.write(row, 5, record.company_id.name if record.company_id else "", formats["text"])
            sheet.write(row, 6, record.journal_id.name if record.journal_id else "", formats["text"])
            sheet.write(row, 7, record.currency_id.name if record.currency_id else "", formats["text"])
            sheet.write(row, 8, record.collected_amount or 0.0, formats["money"])
            sheet.write(row, 9, record.invoice_total or 0.0, formats["money"])
            sheet.write(row, 10, record.residual_amount or 0.0, formats["money"])
            sheet.write(row, 11, fmt_date(record.invoice_date), formats["date"])
            sheet.write(row, 12, fmt_date(record.due_date), formats["date"])
            sheet.write(row, 13, record.payment_delay_days or 0, formats["integer"])
            sheet.write(row, 14, record.product_names or "", formats["text"])
            sheet.write(row, 15, record.memo or "", formats["text"])

        def generate_xlsx_report(self, workbook, data, records):
            self._log_export(records)

            formats = {
                "header": workbook.add_format({
                    "bold": True, "bg_color": "#0D2137", "font_color": "#FFFFFF",
                    "border": 1, "align": "center", "valign": "vcenter",
                }),
                "date": workbook.add_format({"num_format": "yyyy-mm-dd", "border": 1}),
                "text": workbook.add_format({"border": 1}),
                "money": workbook.add_format({"num_format": "#,##0.00", "border": 1}),
                "integer": workbook.add_format({"num_format": "0", "border": 1, "align": "center"}),
                "group": workbook.add_format({
                    "bold": True, "bg_color": "#0F2D4A", "font_color": "#00B89C", "border": 1,
                }),
                "total": workbook.add_format({
                    "bold": True, "bg_color": "#E8F8F5", "border": 1, "num_format": "#,##0.00",
                }),
            }

            sheet = workbook.add_worksheet(_("Reconciliation"))
            sheet.freeze_panes(1, 0)
            sheet.set_column(0, 0, 14)
            sheet.set_column(1, 2, 22)
            sheet.set_column(3, 4, 24)
            sheet.set_column(5, 7, 18)
            sheet.set_column(8, 10, 16)
            sheet.set_column(11, 12, 14)
            sheet.set_column(13, 13, 12)
            sheet.set_column(14, 15, 28)

            self._write_header(sheet, workbook, formats)

            groups = self._group_records(records)
            row = 1
            for label, group in groups:
                if label and len(groups) > 1:
                    sheet.merge_range(row, 0, row, 15, label, formats["group"])
                    row += 1
                for record in group:
                    self._write_record(sheet, row, record, formats)
                    row += 1
                if label and len(groups) > 1:
                    sheet.write(row, 7, _("Subtotal"), formats["total"])
                    sheet.write(row, 8, sum(r.collected_amount or 0 for r in group), formats["total"])
                    sheet.write(row, 9, sum(r.invoice_total or 0 for r in group), formats["total"])
                    sheet.write(row, 10, sum(r.residual_amount or 0 for r in group), formats["total"])
                    row += 1

            if records:
                sheet.write(row, 7, _("Grand Total"), formats["total"])
                sheet.write(row, 8, sum(r.collected_amount or 0 for r in records), formats["total"])
                sheet.write(row, 9, sum(r.invoice_total or 0 for r in records), formats["total"])
                sheet.write(row, 10, sum(r.residual_amount or 0 for r in records), formats["total"])

            try:
                company = self.env.company
                if company.logo:
                    logo_data = base64.b64decode(company.logo)
                    sheet.insert_image("P1", "logo.png", {
                        "image_data": BytesIO(logo_data), "x_scale": 0.5, "y_scale": 0.5,
                    })
            except Exception:
                pass

    return CollectionReconciliationReportXlsx


# Execute at import time — the returned class (or None) is what Odoo's module
# loader picks up.  When report_xlsx is absent, nothing is registered and the
# module still installs cleanly.
_XlsxClass = _build_xlsx_class()
