from odoo import api, http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


class WebsiteForm(http.Controller):
    @http.route(['/warranty'], type='http', auth="user", website=True)
    def warranty(self, **kw):
        warranty_request = request.env['product.warranty.model'].sudo().search(
            [])
        invoices = request.env['account.move'].sudo().search([])
        customer = request.env['res.partner'].sudo().search([])
        products_with_warranty = request.env['product.product'].sudo().search([
            ('warranty_exist', '=', True),
        ])

        lot_number = request.env['stock.lot'].sudo().search([])

        values = {
            'warranty_id': warranty_request,
            'invoice_id': invoices,
            'customer_id': customer,
            'product_id': products_with_warranty,  # Only pass filtered products
            'lot_num_id': lot_number,
        }
        # print(values)

        return request.render("product_warranty.online_warranty_request_form",
                              values)

    @http.route(['/warranty/form/submit'], type='http', auth="user",
                website=True,
                method=['POST'])
    def submit_warranty_request(self, **post):
        product_id = post.get('product_id')
        lot_num_id = post.get('lot_num_id')
        invoice = post.get('invoice_id')

        # Create a warranty request
        warranty = request.env['product.warranty.model'].sudo().create({
            'product_id': int(product_id),
            'lot_num_id': lot_num_id,
            'invoice_id': invoice,
        })
        warranty.customer_details_id = warranty.invoice_id.partner_id.id
        return request.redirect('/warranty-thank-you')

