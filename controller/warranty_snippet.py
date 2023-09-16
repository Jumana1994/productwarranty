from odoo import api, http
from odoo.http import request


class WebsiteSnippet(http.Controller):
    @http.route(['/warranty_products'], type='json', auth="user",
                website=True)
    def warranty_products(self):
        # Fetch the top 4 warranty products (adjust this query as needed)
        warranty_products = request.env['product.template'].sudo().search_read([
            ('warranty_exist', '=', True)],['id','image_1920', 'name', 'warranty_type',
                                            'warranty_period'], limit=8,
            order='warranty_period DESC')
        return warranty_products
