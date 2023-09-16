# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.exceptions import ValidationError
from datetime import date


class ProductWarrantyReport(models.AbstractModel):
    """Create an abstract model for passing reporting values"""
    _name = "report.product_warranty.report_warranty"
    _description = "Product Warranty Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        """This function to get the pdf report."""
        product_id = tuple(data['product_ids'])
        customer_id = data['customer_id']
        start_date = data['start_date']
        end_date = data['end_date']
        res = len(product_id)

        today_date = date.today()

        if (start_date and end_date and
                start_date > end_date):
            raise ValidationError("From Date cannot be greater than To Date")

        query = """
             SELECT 
             product_warranty_model.name,
             request_date, 
             product_template.name as product_name,
             invoice.name as invoice_name,
             res_partner.name as customer_details_id,
             warranty_exp_date,
             product_warranty_model.states,
             CASE 
                 WHEN product_warranty_model.states = 'draft' THEN 'Draft'
                 WHEN product_warranty_model.states = 'to approve' THEN 'To 
                 approve'
                 WHEN product_warranty_model.states = 'approved' THEN 'Approved'
                 WHEN product_warranty_model.states = 'product received' THEN 
                 'Product Received'
                 WHEN product_warranty_model.states = 'done' THEN 'Done'
                 WHEN product_warranty_model.states = 'cancel' THEN 'Cancel'
             END as states_label
             FROM product_warranty_model 
             INNER JOIN
             product_product ON product_warranty_model.product_id =
              product_product.id
             INNER JOIN 
             product_template ON product_product.product_tmpl_id = 
             product_template.id
             INNER JOIN
             res_partner ON product_warranty_model.customer_details_id =
             res_partner.id 
             INNER JOIN
             account_move AS invoice ON product_warranty_model.invoice_id =
              invoice.id
             """
        if customer_id:
            query += """ where res_partner.id = %d """ % data['customer_id']
        if product_id:
            if res == 1:
                query += (""" and product_warranty_model.product_id = '%d' """
                          % product_id)
            else:
                query += f""" and product_warranty_model.product_id in 
        {product_id} """

        if start_date:
            query += (""" and product_warranty_model.request_date >= '%s' """
                      % start_date)
        if end_date:
            query += (""" and product_warranty_model.request_date <= '%s' """
                      % end_date)

        self.env.cr.execute(query)
        records = self.env.cr.dictfetchall()
        if records:
            return {
                'doc_ids': docids,
                'doc_model': 'warranty.report',
                'data': data,
                'options': records,
                'current_date': today_date,

            }
        else:
            raise ValidationError("No records available")
