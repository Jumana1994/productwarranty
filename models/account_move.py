# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    """add warranty info page after other info in invoice in account
     move model"""
    _inherit = "account.move"
    warranty_request_ids = fields.One2many('product.warranty.model', 'invoice_id', string='Warranty requests')

    @api.onchange('warranty_request_ids')
    def _onchange_warranty_request_ids(self):
        # Remove the option to add lines when creating or editing warranty requests
        for warranty_info in self.warranty_request_ids:
            warranty_info.unlink()
