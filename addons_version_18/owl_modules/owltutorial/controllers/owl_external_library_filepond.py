from odoo import http
import base64

class OwlExternalLibraryFilePond(http.Controller):

    @http.route('/owl/filepond/process', type='http', auth='user', methods=['POST'], csrf=False)
    def filepond_process(self, **kwargs):

        filepond = http.request.httprequest.files.get('filepond')

        if not filepond:
            return http.request.make_response("No file", status=400)

        file_content = filepond.read()

        attachment = http.request.env['ir.attachment'].sudo().create({
            'name': filepond.filename,
            'datas': base64.b64encode(file_content),
            'type': 'binary',
            'mimetype': filepond.content_type,
        })

        return str(attachment.id)

    @http.route('/owl/filepond/revert', type='http', auth='user', methods=['DELETE'], csrf=False)
    def filepond_revert(self, **kwargs):
        attachment_id = http.request.httprequest.data.decode("utf-8")

        if attachment_id:
            http.request.env['ir.attachment'].sudo().browse(
                int(attachment_id)
            ).unlink()

        return "OK"
