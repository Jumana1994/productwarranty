# -*- coding: utf-8 -*-
from odoo import fields, models
from datetime import date
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
import io
import json

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class WarrantyReport(models.TransientModel):
    _name = 'warranty.report'
    _description = 'Warranty Report'
    product_ids = fields.Many2many('product.product',
                                   string="Products")
    customer_id = fields.Many2one('res.partner', string='Customer')
    start_date = fields.Date(string='Start date')
    end_date = fields.Date(string='End date')
    today_date = date.today()

    def action_print(self):
        product_details_id = []
        product_details_name = []
        for rec in self.product_ids:
            product_details_id.append(rec.id)
            product_details_name.append(rec.display_name)
        data = {
            'model_id': self.id,
            'product_ids': product_details_id,
            'products_name': product_details_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'customer_id': self.customer_id.id,
            'customer_name': self.customer_id.name,

        }

        return self.env.ref(
            'product_warranty.action_report_warranty_report'
        ).report_action(None, data=data)

    def print_xlsx(self):
        product_details_id = []
        product_details_name = []
        for rec in self.product_ids:
            product_details_id.append(rec.id)
            product_details_name.append(rec.display_name)
        product_id = tuple(product_details_id)
        customer_id = self.customer_id
        start_date = self.start_date
        end_date = self.end_date
        res = len(product_id)

        today_date = date.today()
        if (self.start_date and self.end_date and
                self.start_date > self.end_date):
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
                         WHEN product_warranty_model.states = 'draft' THEN 
                         'Draft'
                         WHEN product_warranty_model.states = 'to approve' THEN 
                         'To approve'
                         WHEN product_warranty_model.states = 'approved' THEN 
                         'Approved'
                         WHEN product_warranty_model.states = 'product received'
                          THEN 'Product Received'
                         WHEN product_warranty_model.states = 'done' THEN 'Done'
                         WHEN product_warranty_model.states = 'cancel' THEN 
                         'Cancel'
                     END as states_label
                     FROM product_warranty_model 
                     INNER JOIN
                     product_product ON product_warranty_model.product_id = 
                     product_product.id
                     INNER JOIN 
                     product_template ON product_product.product_tmpl_id =
                      product_template.id
                     INNER JOIN
                     res_partner ON product_warranty_model.customer_details_id 
                     =res_partner.id 
                     INNER JOIN
                     account_move AS invoice ON product_warranty_model.invoice_id 
                     = invoice.id
                     """
        if customer_id:
            query += """ where res_partner.id = %d """ % customer_id
        if product_id:
            if res == 1:
                query += (""" and product_warranty_model.product_id = '%d' """ %
                          product_id)
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
        data = {
            'model_id': self.id,
            'product_ids': product_details_id,
            'products_name': product_details_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'customer_id': self.customer_id.id,
            'customer_name': self.customer_id.name,
            'options': records,
            'current_date': today_date,

        }
        if records:
            return {
                'type': 'ir.actions.report',
                'data': {'model': 'warranty.report',
                         'options': json.dumps(data,
                                               default=date_utils.json_default),
                         'output_format': 'xlsx',
                         'report_name': 'Excel Report',
                         },

                'report_type': 'xlsx',
            }
        else:
            raise ValidationError("No records available")

    def get_xlsx_report(self, data, response):
        product_ids = data['product_ids']
        product_name = data['products_name']
        customer_id = data['customer_name']
        start_date = data['start_date']
        end_date = data['end_date']
        today_date = data['current_date']

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        headings = workbook.add_format(
            {'font_size': '11px', 'font_color': '#FFFFFF', 'align': 'center',
             'bold': True, 'bg_color': '#000000'})
        normal = workbook.add_format({'font_size': '10px', 'align': 'center'})
        sheet.merge_range('B2:I3', 'PRODUCT WARRANTY', head)
        sheet.merge_range('A8:B8', 'Printed date:', cell_format)
        sheet.merge_range('C8:D8', today_date, normal)
        if start_date:
            sheet.merge_range('A4:B4', 'From Date:', cell_format)
            sheet.merge_range('C4:D4', start_date, normal)
        if end_date:
            sheet.merge_range('A5:B5', 'To Date:', cell_format)
            sheet.merge_range('C5:D5', end_date, normal)
        if customer_id:
            sheet.merge_range('A6:B6', 'Customer:', normal)
            sheet.merge_range('C6:D6', customer_id, cell_format)
        if len(product_ids) or len(product_ids) > 1:
            product_id_str = ', '.join(product_name)
            sheet.merge_range('A7:B7', 'Product:', normal)
            sheet.merge_range('C7:E7', product_id_str, cell_format)

        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        row = 10
        col = 0
        sheet.write(row, col, 'Sequence No', headings)
        sheet.write(row, col + 1, 'Request date', headings)
        sheet.write(row, col + 2, 'Product Name', headings)
        sheet.write(row, col + 3, 'Invoice Reference', headings)
        if customer_id:
            sheet.write(row, col + 4, 'Warranty Expiration', headings)
            sheet.write(row, col + 5, 'State', headings)
        else:
            sheet.write(row, col + 4, 'Customer', headings)
            sheet.write(row, col + 5, 'Warranty Expiration', headings)
            sheet.write(row, col + 6, 'State', headings)
        for rec in data['options']:
            row += 1
            sheet.write(row, col, rec['name'], cell_format)
            sheet.write(row, col + 1, rec['request_date'], cell_format)
            sheet.write(row, col + 2, rec['product_name']['en_US'],
                        cell_format)
            sheet.write(row, col + 3, rec['invoice_name'], cell_format)
            if customer_id:
                sheet.write(row, col + 4, rec['warranty_exp_date'], cell_format)
                sheet.write(row, col + 5, rec['states_label'], cell_format)
            else:
                sheet.write(row, col + 4, rec['customer_details_id'],
                            cell_format)
                sheet.write(row, col + 5, rec['warranty_exp_date'],
                            cell_format)
                sheet.write(row, col + 6, rec['states_label'], cell_format)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
