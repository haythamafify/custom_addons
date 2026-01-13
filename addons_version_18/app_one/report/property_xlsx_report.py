# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging
import io
import xlsxwriter
from datetime import datetime

_logger = logging.getLogger(__name__)


class PropertyXlsxReportController(http.Controller):

    @http.route('/property/xlsx_report', type='http', auth='user', csrf=False)
    def download_property_xlsx_report(self, property_ids=None, **kw):
        """
        Controller لتحميل تقرير Excel للعقارات

        :param property_ids: قائمة معرفات العقارات (JSON string)
        """
        try:
            _logger.info("========== Starting Excel Report Generation ==========")

            # تحويل property_ids من JSON string إلى list
            if property_ids:
                property_ids = json.loads(property_ids)
                _logger.info(f"Property IDs received: {property_ids}")
            else:
                property_ids = []
                _logger.info("No property IDs provided, will export all")

            # جلب العقارات
            if property_ids:
                properties = request.env['property'].browse(property_ids)
            else:
                properties = request.env['property'].search([])

            _logger.info(f"Found {len(properties)} properties to export")

            # ========== إنشاء ملف Excel ==========
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            sheet = workbook.add_worksheet('Properties Report')

            # ========== التنسيقات ==========
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#2C3E50',
                'font_color': 'white',
                'border': 2
            })

            header_format = workbook.add_format({
                'bold': True,
                'font_size': 11,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#3498DB',
                'font_color': 'white',
                'border': 1,
                'text_wrap': True
            })

            cell_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'font_size': 10
            })

            number_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '#,##0.00',
                'font_size': 10
            })

            # تنسيقات الحالات
            state_formats = {
                'draft': workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1,
                    'bg_color': '#95A5A6',
                    'font_color': 'white',
                    'bold': True
                }),
                'pending': workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1,
                    'bg_color': '#F39C12',
                    'font_color': 'white',
                    'bold': True
                }),
                'sold': workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1,
                    'bg_color': '#27AE60',
                    'font_color': 'white',
                    'bold': True
                }),
                'closed': workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1,
                    'bg_color': '#E74C3C',
                    'font_color': 'white',
                    'bold': True
                })
            }

            positive_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '#,##0.00',
                'font_color': '#27AE60',
                'bold': True
            })

            negative_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '#,##0.00',
                'font_color': '#E74C3C',
                'bold': True
            })

            late_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'bg_color': '#E74C3C',
                'font_color': 'white',
                'bold': True
            })

            # ========== كتابة العنوان ==========
            report_title = f'Properties Report - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            sheet.merge_range('A1:N1', report_title, title_format)

            # ========== كتابة العناوين ==========
            headers = [
                'Ref',
                'Property Name',
                'Postcode',
                'State',
                'Bedrooms',
                'Living Area (m²)',
                'Facades',
                'Garage',
                'Garden',
                'Expected Price',
                'Selling Price',
                'Difference',
                'Owner',
                'Responsible'
            ]

            for col, header in enumerate(headers):
                sheet.write(1, col, header, header_format)

            # ========== كتابة البيانات ==========
            row = 2

            if not properties:
                sheet.merge_range(f'A{row}:N{row}', 'No properties found', cell_format)
            else:
                for prop in properties:
                    # Ref
                    sheet.write(row, 0, prop.ref or '', cell_format)

                    # Name
                    sheet.write(row, 1, prop.name or '', cell_format)

                    # Postcode
                    sheet.write(row, 2, prop.postcode or '', cell_format)

                    # State
                    state_display = dict(prop._fields['state'].selection).get(prop.state, '')
                    state_fmt = state_formats.get(prop.state, cell_format)
                    sheet.write(row, 3, state_display, state_fmt)

                    # Bedrooms
                    sheet.write(row, 4, prop.bedrooms or 0, number_format)

                    # Living Area
                    sheet.write(row, 5, prop.living_area or 0, number_format)

                    # Facades
                    sheet.write(row, 6, prop.facades or 0, number_format)

                    # Garage
                    sheet.write(row, 7, 'Yes' if prop.garage else 'No', cell_format)

                    # Garden
                    sheet.write(row, 8, 'Yes' if prop.garden else 'No', cell_format)

                    # Expected Price
                    sheet.write(row, 9, prop.expected_price or 0, number_format)

                    # Selling Price
                    sheet.write(row, 10, prop.selling_price or 0, number_format)

                    # Difference
                    diff_fmt = positive_format if prop.diff >= 0 else negative_format
                    sheet.write(row, 11, prop.diff, diff_fmt)

                    # Owner
                    sheet.write(row, 12, prop.owner_id.name if prop.owner_id else '', cell_format)

                    # Responsible
                    responsible_text = prop.user_id.name if prop.user_id else ''
                    if prop.is_late:
                        sheet.write(row, 13, f'{responsible_text} (LATE)', late_format)
                    else:
                        sheet.write(row, 13, responsible_text, cell_format)

                    row += 1

            # ========== صف الملخص ==========
            if properties:
                summary_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#34495E',
                    'font_color': 'white',
                    'border': 2,
                    'align': 'center',
                    'num_format': '#,##0.00'
                })

                row += 1
                sheet.merge_range(f'A{row}:D{row}', f'SUMMARY - Total Properties: {len(properties)}', summary_format)
                sheet.write(row, 4, '', summary_format)
                sheet.write(row, 5, '', summary_format)
                sheet.write(row, 6, '', summary_format)
                sheet.write(row, 7, '', summary_format)
                sheet.write(row, 8, '', summary_format)

                total_expected = sum(p.expected_price for p in properties)
                total_selling = sum(p.selling_price for p in properties)
                total_diff = total_selling - total_expected

                sheet.write(row, 9, total_expected, summary_format)
                sheet.write(row, 10, total_selling, summary_format)
                sheet.write(row, 11, total_diff, summary_format)
                sheet.write(row, 12, '', summary_format)
                sheet.write(row, 13, '', summary_format)

            # ========== ضبط عرض الأعمدة ==========
            sheet.set_column('A:A', 12)
            sheet.set_column('B:B', 30)
            sheet.set_column('C:C', 12)
            sheet.set_column('D:D', 12)
            sheet.set_column('E:H', 12)
            sheet.set_column('I:K', 15)
            sheet.set_column('L:L', 15)
            sheet.set_column('M:N', 20)

            # ========== تجميد الصفوف ==========
            sheet.freeze_panes(2, 0)

            # ========== فلاتر تلقائية ==========
            if properties:
                sheet.autofilter(1, 0, row - 1, len(headers) - 1)

            # ========== إغلاق الملف ==========
            workbook.close()
            output.seek(0)
            xlsx_data = output.read()
            output.close()

            # ========== إرسال الاستجابة ==========
            filename = f'Properties_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

            _logger.info(f"Report generated successfully: {filename}")

            return request.make_response(
                xlsx_data,
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', f'attachment; filename={filename}')
                ]
            )

        except Exception as e:
            _logger.error(f"Error generating XLSX report: {str(e)}", exc_info=True)
            return request.make_response(
                f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>",
                headers=[('Content-Type', 'text/html')],
                status=500
            )