import io
from ast import literal_eval

import xlsxwriter
from odoo import http
from odoo.http import request


class ExcelPropertyReport(http.Controller):
    @http.route('/property/excel/report/<string:property_ids>', type="http", auth="user")
    def download_property_excell(self, property_ids):

        property_ids = request.env['property'].browse(literal_eval(property_ids))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': "True"})
        worksheet = workbook.add_worksheet("properties")
        header_format = workbook.add_format({"bold": True, 'bg_color': '#D30303', 'border': 1, 'align': 'center'})
        string_format = workbook.add_format({'border': 1, 'align': 'center'})
        price_format = workbook.add_format({'num_format': "$##,##00.00", 'border': 1, 'align': 'center'})
        headers = ['name', 'description', 'postcode', 'selling_price', 'garden', 'garage']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)
        row_num = 1
        for all_property in property_ids:
            worksheet.write(row_num, 0, all_property.name, string_format)
            worksheet.write(row_num, 1, all_property.description, string_format)
            worksheet.write(row_num, 2, all_property.postcode, string_format)
            worksheet.write(row_num, 3, all_property.selling_price, price_format)
            worksheet.write(row_num, 4, 'Yes' if all_property.garden else "No", string_format)
            worksheet.write(row_num, 5, 'Yes' if all_property.garage else "No", string_format)
            row_num += 1


        workbook.close()
        output.seek(0)
        file_name = "property report.xlsx"
        return request.make_response(
            output.getvalue(),
            headers=[
                ('content-type', 'application/vnd.openxmlformats-officedocumnt.spreadsheetml.sheet'),
                ('content-Disposition', f'attachment;filename={file_name}')
            ]
        )
